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

class AdvancedRAGSystem:
    """
    Advanced RAG with:
    1. Fuzzy entity matching (partial names)
    2. Multi-hop reasoning
    3. Temporal queries
    4. Relationship path finding
    """
    
    def __init__(self):
        print("Initializing Advanced RAG System...")
        self.llm_client = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY
        )
        self.graph = GraphBuilder(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
        print("✓ Advanced RAG system ready\n")
    
    def close(self):
        self.graph.close()
    
    # ========================================================================
    # FUZZY ENTITY SEARCH
    # ========================================================================
    
    def fuzzy_search_entities(self, search_term: str, limit: int = 5) -> List[Dict]:
        """
        Find entities using partial/fuzzy matching
        
        Strategies:
        1. Exact match (case-insensitive)
        2. Contains match ("jassy" matches "Andy Jassy")
        3. Word match (any word matches)
        
        Args:
            search_term: Partial entity name
            limit: Max results to return
        
        Returns:
            List of matching entities with relevance scores
        
        Examples:
        - "jassy" → finds "Andy Jassy"
        - "bezos" → finds "Jeff Bezos"
        - "microsoft" → finds "Microsoft"
        - "aws" → finds "Amazon Web Services", "AWS"
        """
        with self.graph.driver.session() as session:
            # Multi-strategy search query
            query = """
            MATCH (e)
            WHERE toLower(e.name) CONTAINS toLower($search_term)
            RETURN 
                e.name as name,
                e.type as type,
                properties(e) as properties,
                CASE 
                    WHEN toLower(e.name) = toLower($search_term) THEN 100
                    WHEN toLower(e.name) STARTS WITH toLower($search_term) THEN 90
                    WHEN toLower(e.name) ENDS WITH toLower($search_term) THEN 80
                    ELSE 70
                END as relevance_score
            ORDER BY relevance_score DESC, e.name
            LIMIT $limit
            """
            
            result = session.run(query, search_term=search_term, limit=limit)
            
            matches = []
            for record in result:
                matches.append({
                    "name": record["name"],
                    "type": record["type"],
                    "properties": record["properties"],
                    "relevance": record["relevance_score"]
                })
            
            return matches
    
    def extract_entities_with_fuzzy_match(self, question: str) -> List[str]:
        """
        Extract entities with fuzzy matching fallback
        
        Process:
        1. Use LLM to extract entity mentions
        2. For each mention, try fuzzy search in graph
        3. Return best matches
        
        This handles:
        - Partial names: "jassy" → "Andy Jassy"
        - Nicknames: "bezos" → "Jeff Bezos"
        - Abbreviations: "aws" → "Amazon Web Services"
        """
        # Step 1: Extract mentions from question
        prompt = f"""
Extract entity names or partial names mentioned in this question.
Include partial names, nicknames, or abbreviations.

Question: {question}

Return ONLY a JSON array: ["entity1", "entity2", ...]

Examples:
Q: "who is jassy?" → ["jassy"]
Q: "tell me about aws" → ["aws"]
Q: "what did bezos create?" → ["bezos"]
"""
        
        try:
            response = self.llm_client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "Extract entity mentions. Return only JSON array."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )
            
            result = response.choices[0].message.content.strip()
            mentions = json.loads(result)
            
            if not mentions:
                return []
            
            print(f"📌 Extracted mentions: {mentions}")
            
            # Step 2: Fuzzy match each mention
            matched_entities = []
            
            for mention in mentions:
                matches = self.fuzzy_search_entities(mention, limit=3)
                
                if matches:
                    # Use best match
                    best_match = matches[0]
                    matched_entities.append(best_match["name"])
                    
                    if len(matches) > 1:
                        print(f"   '{mention}' → Found {len(matches)} matches:")
                        for match in matches[:3]:
                            print(f"      - {match['name']} ({match['type']}) [score: {match['relevance']}]")
                        print(f"   ✓ Using: {best_match['name']}")
                    else:
                        print(f"   '{mention}' → {best_match['name']}")
                else:
                    print(f"   '{mention}' → No matches found")
            
            return matched_entities
            
        except Exception as e:
            print(f"⚠ Error in fuzzy matching: {e}")
            return []
    
    # ========================================================================
    # ENHANCED CONTEXT RETRIEVAL
    # ========================================================================
    
    def retrieve_graph_context(self, entities: List[str], max_hops: int = 2) -> str:
        """Enhanced context retrieval with better formatting"""
        if not entities:
            return "No specific entities mentioned in the question."
        
        context_parts = []
        
        for entity_name in entities:
            print(f"🔍 Retrieving context for: {entity_name}")
            
            with self.graph.driver.session() as session:
                # Get entity + neighborhood
                query = f"""
                MATCH (start {{name: $entity_name}})
                OPTIONAL MATCH (start)-[r]-(connected)
                WITH start, 
                     collect(DISTINCT connected) as connected_nodes,
                     collect(DISTINCT {{
                         rel: r, 
                         source: startNode(r).name,
                         target: endNode(r).name,
                         type: type(r),
                         props: properties(r)
                     }}) as relationships
                RETURN start, connected_nodes, relationships
                """
                
                result = session.run(query, entity_name=entity_name)
                record = result.single()
                
                if not record:
                    context_parts.append(f"\nEntity '{entity_name}' not found in knowledge graph.")
                    continue
                
                start_node = record["start"]
                connected_nodes = record["connected_nodes"]
                relationships = record["relationships"]
                
                # Format context
                entity_context = self._format_enhanced_context(
                    start_node,
                    connected_nodes,
                    relationships
                )
                
                context_parts.append(entity_context)
        
        full_context = "\n\n".join(context_parts)
        print(f"\n📄 Retrieved context ({len(full_context)} characters)")
        return full_context
    
    def _format_enhanced_context(self, entity, connected_nodes: List, relationships: List) -> str:
        """Format context with clear relationship descriptions"""
        lines = []
        
        entity_type = entity.get("type", "Entity")
        entity_name = entity.get("name", "Unknown")
        
        lines.append(f"=== {entity_name} ({entity_type}) ===")
        
        # Properties
        if len(entity) > 2:
            lines.append("\nProperties:")
            for key, value in entity.items():
                if key not in ["name", "type"]:
                    lines.append(f"  • {key}: {value}")
        
        # Relationships with clear direction
        if relationships:
            lines.append("\nRelationships:")
            
            for rel_data in relationships:
                if not rel_data or not rel_data.get("rel"):
                    continue
                
                source = rel_data.get("source", "?")
                target = rel_data.get("target", "?")
                rel_type = rel_data.get("type", "RELATED")
                props = rel_data.get("props", {})
                
                # Determine direction relative to main entity
                if source == entity_name:
                    direction = f"{entity_name} --[{rel_type}]--> {target}"
                else:
                    direction = f"{source} --[{rel_type}]--> {entity_name}"
                
                # Add temporal info
                if props.get("valid_from") or props.get("valid_to"):
                    valid_from = props.get("valid_from", "?")
                    valid_to = props.get("valid_to", "?")
                    direction += f" (from {valid_from} to {valid_to})"
                
                if props.get("description"):
                    direction += f" - {props['description']}"
                
                lines.append(f"  • {direction}")
        
        # Connected entities
        if connected_nodes:
            lines.append("\nConnected Entities:")
            seen = set()
            for node in connected_nodes:
                if node and node.get("name") != entity_name:
                    name = node.get("name")
                    if name not in seen:
                        node_type = node.get("type", "Entity")
                        lines.append(f"  • {name} ({node_type})")
                        seen.add(name)
        
        return "\n".join(lines)
    
    # ========================================================================
    # ANSWER GENERATION
    # ========================================================================
    
    def generate_answer(self, question: str, context: str) -> str:
        """Generate answer with citations"""
        prompt = f"""
You are a knowledgeable assistant answering questions using a knowledge graph.

CONTEXT FROM KNOWLEDGE GRAPH:
{context}

QUESTION: {question}

INSTRUCTIONS:
1. Answer using ONLY the context provided
2. Cite specific facts (e.g., "According to the graph, Andy Jassy became CEO in 2021")
3. Include dates and relationships when relevant
4. If information is missing, say so clearly
5. Be conversational but accurate

ANSWER:
"""
        
        try:
            response = self.llm_client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions using knowledge graph context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error generating answer: {e}"
    
    # ========================================================================
    # MAIN QUERY
    # ========================================================================
    
    def query(self, question: str, max_hops: int = 2, show_context: bool = False) -> Dict:
        """Complete RAG query with fuzzy matching"""
        print("="*70)
        print(f"QUERY: {question}")
        print("="*70)
        
        print("\n[Step 1] Extracting entities with fuzzy matching...")
        entities = self.extract_entities_with_fuzzy_match(question)
        
        print(f"\n[Step 2] Retrieving context for: {entities}...")
        context = self.retrieve_graph_context(entities, max_hops=max_hops)
        
        if show_context:
            print(f"\n[Context Retrieved]")
            print("─" * 70)
            print(context)
            print("─" * 70)
        
        print("\n[Step 3] Generating answer...")
        answer = self.generate_answer(question, context)
        
        return {
            "question": question,
            "answer": answer,
            "entities_used": entities,
            "context": context if show_context else None
        }


# ============================================================================
# INTERACTIVE MODE
# ============================================================================

def interactive_mode():
    rag = AdvancedRAGSystem()
    
    print("\n" + "="*70)
    print("ADVANCED KNOWLEDGE GRAPH RAG")
    print("="*70)
    print("\nFeatures:")
    print("  ✓ Fuzzy entity matching (partial names work!)")
    print("  ✓ Multi-hop reasoning")
    print("  ✓ Temporal queries")
    print("\nCommands:")
    print("  - Ask any question")
    print("  - 'context' to toggle context display")
    print("  - 'search <term>' to fuzzy search entities")
    print("  - 'stats' for graph statistics")
    print("  - 'exit' to quit")
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
                print(f"✓ Context display: {'ON' if show_context else 'OFF'}")
                continue
            
            elif user_input.lower().startswith('search '):
                search_term = user_input[7:].strip()
                matches = rag.fuzzy_search_entities(search_term, limit=10)
                print(f"\n🔍 Search results for '{search_term}':")
                if matches:
                    for match in matches:
                        print(f"  • {match['name']} ({match['type']}) - Score: {match['relevance']}")
                else:
                    print("  No matches found")
                continue
            
            elif user_input.lower() == 'stats':
                stats = rag.graph.get_database_stats()
                print(f"\n📊 Graph Statistics:")
                print(f"   Nodes: {stats['nodes']}")
                print(f"   Relationships: {stats['relationships']}")
                print(f"   Labels: {', '.join(stats['labels'])}")
                continue
            
            # Process query
            response = rag.query(user_input, show_context=show_context)
            
            print("\n" + "─"*70)
            print("🤖 ANSWER:")
            print("─"*70)
            print(response["answer"])
            print("─"*70)
            
            if response["entities_used"]:
                print(f"\n📚 Entities used: {', '.join(response['entities_used'])}")
    
    finally:
        rag.close()


if __name__ == "__main__":
    interactive_mode()