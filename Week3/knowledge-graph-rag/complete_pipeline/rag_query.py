from openai import OpenAI
from typing import List, Dict, Optional
from config import (
    OPENROUTER_API_KEY, 
    OPENROUTER_BASE_URL, 
    MODEL_NAME,
    NEO4J_URI,
    NEO4J_USERNAME,
    NEO4J_PASSWORD
)
from graph_builder import GraphBuilder
import json

class RAGQuerySystem:
    def __init__(self):
        print("Initializing RAG Query System...")
        self.llm_client = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY
        )
        self.graph = GraphBuilder(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
        print("✓ RAG system ready\n")
    
    def close(self):
        self.graph.close()
    
    def extract_entities_from_question(self, question: str) -> List[str]:
        prompt = f"""
Extract entity names mentioned in this question. Return ONLY a JSON array of entity names.
Use proper capitalization for entity names (e.g., "Amazon" not "amazon", "Jeff Bezos" not "jeff bezos").

Question: {question}

Return format: ["Entity1", "Entity2", ...]

If no specific entities are mentioned, return an empty array: []

Examples:
Q: "Who founded Amazon?" → ["Amazon"]
Q: "What did Jeff Bezos create?" → ["Jeff Bezos"]
Q: "Tell me about cloud computing companies" → []
Q: "what is amazon?" → ["Amazon"]
Q: "tell me about microsoft" → ["Microsoft"]
"""
        
        try:
            response = self.llm_client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a precise entity extraction system. Return only JSON with properly capitalized entity names."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )
            
            result = response.choices[0].message.content.strip()
            entities = json.loads(result)
            print(f"📌 Extracted entities: {entities}")
            return entities if isinstance(entities, list) else []
            
        except Exception as e:
            print(f"⚠ Error extracting entities: {e}")
            return []
    
    def retrieve_graph_context(self, entities: List[str], max_hops: int = 2) -> str:
        if not entities:
            return "No specific entities mentioned in the question."
        
        context_parts = []
        
        for entity_name in entities:
            print(f"🔍 Retrieving context for: {entity_name}")
            
            with self.graph.driver.session() as session:
                # Case-insensitive entity matching
                query = f"""
                MATCH (start)
                WHERE toLower(start.name) = toLower($entity_name)
                OPTIONAL MATCH path = (start)-[*1..{max_hops}]-(connected)
                WITH start, 
                     collect(DISTINCT connected) as connected_nodes,
                     collect(DISTINCT relationships(path)) as all_relationships
                RETURN 
                    start,
                    connected_nodes,
                    all_relationships
                LIMIT 1
                """
                
                result = session.run(query, entity_name=entity_name)
                record = result.single()
                
                if not record:
                    context_parts.append(f"\nEntity '{entity_name}' not found in knowledge graph.")
                    continue
                
                start_node = record["start"]
                connected_nodes = record["connected_nodes"]
                all_relationships = record["all_relationships"]
                
                entity_context = self._format_entity_context(
                    start_node, 
                    connected_nodes, 
                    all_relationships
                )
                
                context_parts.append(entity_context)
        
        full_context = "\n\n".join(context_parts)
        print(f"\n📄 Retrieved context ({len(full_context)} characters)")
        return full_context
    
    def _format_entity_context(self, entity, connected_nodes: List, relationships: List) -> str:
        lines = []
        
        entity_type = entity.get("type", "Entity")
        entity_name = entity.get("name", "Unknown")
        
        lines.append(f"Entity: {entity_name} ({entity_type})")
        
        if len(entity) > 2:
            lines.append("Properties:")
            for key, value in entity.items():
                if key not in ["name", "type"]:
                    lines.append(f"- {key}: {value}")
        
        if relationships:
            lines.append("\nRelationships:")
            flat_rels = []
            for rel_list in relationships:
                if rel_list:
                    if isinstance(rel_list, list):
                        flat_rels.extend(rel_list)
                    else:
                        flat_rels.append(rel_list)
            
            seen_rels = set()
            for rel in flat_rels:
                rel_type = rel.type
                rel_props = dict(rel)
                rel_str = f"- {rel_type} relationship"
                
                if "valid_from" in rel_props or "valid_to" in rel_props:
                    valid_from = rel_props.get("valid_from", "?")
                    valid_to = rel_props.get("valid_to", "?")
                    rel_str += f" [{valid_from} → {valid_to}]"
                
                if rel_str not in seen_rels:
                    lines.append(rel_str)
                    seen_rels.add(rel_str)
        
        if connected_nodes:
            lines.append("\nConnected Entities:")
            seen_entities = set()
            
            for node in connected_nodes:
                if node:
                    node_name = node.get("name", "Unknown")
                    node_type = node.get("type", "Entity")
                    
                    if node_name not in seen_entities:
                        node_str = f"- {node_name} ({node_type})"
                        
                        key_props = []
                        for key, value in node.items():
                            if key not in ["name", "type"] and len(key_props) < 2:
                                key_props.append(f"{key}: {value}")
                        
                        if key_props:
                            node_str += f": {', '.join(key_props)}"
                        
                        lines.append(node_str)
                        seen_entities.add(node_name)
        
        return "\n".join(lines)
    
    def generate_answer(self, question: str, context: str) -> str:
        prompt = f"""
You are a helpful assistant answering questions based on a knowledge graph.

Use ONLY the information provided in the context below to answer the question.
If the context doesn't contain enough information, say so clearly.
Cite specific entities and relationships from the context in your answer.

CONTEXT FROM KNOWLEDGE GRAPH:
{context}

QUESTION:
{question}

INSTRUCTIONS:
1. Answer based ONLY on the provided context
2. Cite which entities and relationships you used
3. If information is not in the context, say "The knowledge graph doesn't contain information about..."
4. Include temporal information (dates) when relevant
5. Be concise but complete

ANSWER:
"""
        
        try:
            response = self.llm_client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a precise question-answering system that uses knowledge graph context to provide accurate, cited answers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            answer = response.choices[0].message.content.strip()
            return answer
            
        except Exception as e:
            return f"Error generating answer: {e}"
    
    def query(self, question: str, max_hops: int = 2, show_context: bool = False) -> Dict:
        print("="*70)
        print(f"QUERY: {question}")
        print("="*70)
        
        print("\n[Step 1] Extracting entities from question...")
        entities = self.extract_entities_from_question(question)
        
        print("\n[Step 2] Retrieving context from knowledge graph...")
        context = self.retrieve_graph_context(entities, max_hops=max_hops)
        
        if show_context:
            print(f"\n[Context Retrieved]")
            print("─" * 70)
            print(context)
            print("─" * 70)
        
        print("\n[Step 3] Generating answer...")
        answer = self.generate_answer(question, context)
        
        response = {
            "question": question,
            "answer": answer,
            "entities_used": entities
        }
        
        if show_context:
            response["context"] = context
        
        return response


def interactive_mode():
    rag = RAGQuerySystem()
    
    print("\n" + "="*70)
    print("KNOWLEDGE GRAPH RAG - INTERACTIVE MODE")
    print("="*70)
    print("\nCommands:")
    print("  - Type your question and press Enter")
    print("  - Type 'context' to toggle context display")
    print("  - Type 'stats' to show graph statistics")
    print("  - Type 'exit' or 'quit' to end")
    print("\n" + "="*70 + "\n")
    
    show_context = False
    
    try:
        while True:
            user_input = input("\n💬 Your question: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            elif user_input.lower() == 'context':
                show_context = not show_context
                status = "ON" if show_context else "OFF"
                print(f"✓ Context display: {status}")
                continue
            
            elif user_input.lower() == 'stats':
                stats = rag.graph.get_database_stats()
                print(f"\n📊 Graph Statistics:")
                print(f"   Nodes: {stats['nodes']}")
                print(f"   Relationships: {stats['relationships']}")
                print(f"   Labels: {', '.join(stats['labels'])}")
                continue
            
            response = rag.query(user_input, show_context=show_context)
            
            print("\n" + "─"*70)
            print("🤖 ANSWER:")
            print("─"*70)
            print(response["answer"])
            print("─"*70)
            
            if response["entities_used"]:
                print(f"\n📚 Based on entities: {', '.join(response['entities_used'])}")
    
    finally:
        rag.close()


if __name__ == "__main__":
    interactive_mode()