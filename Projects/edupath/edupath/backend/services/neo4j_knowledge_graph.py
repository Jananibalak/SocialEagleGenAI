from neo4j import GraphDatabase
from typing import List, Dict, Optional
import spacy
import re
from collections import defaultdict
import os

class Neo4jKnowledgeGraph:
    """
    Build and query knowledge graph in Neo4j from documents
    
    Structure:
    - (Document) nodes for each uploaded file
    - (Concept) nodes for key entities/topics
    - (Chunk) nodes for text chunks
    - Relationships: CONTAINS, MENTIONS, RELATED_TO
    """
    
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        username = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        
        # Load spaCy for entity extraction
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("⚠️ spaCy model not found. Run: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def close(self):
        self.driver.close()
    
    def initialize_mentor_graph(self, mentor_id: int):
        """Initialize graph structure for a mentor"""
        with self.driver.session() as session:
            # Create mentor node
            session.run("""
                MERGE (m:Mentor {mentor_id: $mentor_id})
                SET m.created_at = datetime()
                RETURN m
            """, mentor_id=mentor_id)
            
            print(f"✅ Initialized knowledge graph for mentor {mentor_id}")
    
    def add_document_to_graph(
        self,
        mentor_id: int,
        document_text: str,
        document_name: str,
        chunk_size: int = 500
    ):
        """
        Add document to Neo4j knowledge graph
        
        Creates:
        - Document node
        - Chunk nodes (text segments)
        - Concept nodes (extracted entities)
        - Relationships between them
        """
        
        if not self.nlp:
            print("⚠️ NLP not available, using simple chunking")
            return self._add_document_simple(mentor_id, document_text, document_name, chunk_size)
        
        with self.driver.session() as session:
            # 1. Create Document node
            doc_result = session.run("""
                MATCH (m:Mentor {mentor_id: $mentor_id})
                CREATE (d:Document {
                    name: $name,
                    added_at: datetime(),
                    length: $length
                })
                CREATE (m)-[:HAS_DOCUMENT]->(d)
                RETURN d
            """, mentor_id=mentor_id, name=document_name, length=len(document_text))
            
            # 2. Extract concepts using spaCy
            concepts = self._extract_concepts(document_text)
            print(f"📊 Extracted {len(concepts)} concepts from {document_name}")
            
            # 3. Create Concept nodes
            for concept, details in concepts.items():
                session.run("""
                    MATCH (d:Document {name: $doc_name})
                    MERGE (c:Concept {name: $concept})
                    SET c.type = $type,
                        c.frequency = $frequency
                    MERGE (d)-[:MENTIONS {count: $frequency}]->(c)
                """, 
                    doc_name=document_name,
                    concept=concept,
                    type=details['type'],
                    frequency=details['frequency']
                )
            
            # 4. Create text chunks
            chunks = self._chunk_text(document_text, chunk_size)
            
            for i, chunk_text in enumerate(chunks):
                # Extract concepts in this chunk
                chunk_concepts = self._extract_concepts(chunk_text)
                
                # Create Chunk node
                session.run("""
                    MATCH (d:Document {name: $doc_name})
                    CREATE (ch:Chunk {
                        index: $index,
                        text: $text,
                        total_chunks: $total
                    })
                    CREATE (d)-[:CONTAINS]->(ch)
                """,
                    doc_name=document_name,
                    index=i,
                    text=chunk_text,
                    total=len(chunks)
                )
                
                # Link chunk to concepts it mentions
                for concept in chunk_concepts.keys():
                    session.run("""
                        MATCH (ch:Chunk {text: $text})
                        MATCH (c:Concept {name: $concept})
                        MERGE (ch)-[:MENTIONS]->(c)
                    """, text=chunk_text, concept=concept)
            
            print(f"✅ Added {len(chunks)} chunks with {len(concepts)} concepts to knowledge graph")
            
            return len(chunks)
    
    def _extract_concepts(self, text: str) -> Dict:
        """
        Extract key concepts (entities) from text using NLP
        
        Returns:
            Dict of {concept: {type, frequency}}
        """
        if not self.nlp:
            return {}
        
        # Process text with spaCy
        doc = self.nlp(text[:10000])  # Limit for performance
        
        concepts = defaultdict(lambda: {'frequency': 0, 'type': 'UNKNOWN'})
        
        # Extract named entities
        for ent in doc.ents:
            if len(ent.text) > 2:  # Skip very short entities
                concept_name = ent.text.lower()
                concepts[concept_name]['frequency'] += 1
                concepts[concept_name]['type'] = ent.label_
        
        # Extract important noun chunks
        for chunk in doc.noun_chunks:
            if len(chunk.text) > 3 and chunk.root.pos_ == 'NOUN':
                concept_name = chunk.text.lower()
                concepts[concept_name]['frequency'] += 1
                if concepts[concept_name]['type'] == 'UNKNOWN':
                    concepts[concept_name]['type'] = 'TOPIC'
        
        # Filter: keep only concepts mentioned at least 2 times
        filtered = {
            k: v for k, v in concepts.items() 
            if v['frequency'] >= 2
        }
        
        return filtered
    
    def query_knowledge_graph(
        self,
        mentor_id: int,
        query: str,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Query Neo4j knowledge graph using Cypher
        
        Strategy:
        1. Extract concepts from query
        2. Find matching concepts in graph
        3. Retrieve connected chunks
        4. Rank by relevance
        """
        
        if not self.nlp:
            return self._query_simple(mentor_id, query, top_k)
        
        # Extract concepts from query
        query_concepts = self._extract_concepts(query)
        query_keywords = list(query_concepts.keys())
        
        if not query_keywords:
            # Fallback to simple keyword search
            query_keywords = [w.lower() for w in query.split() if len(w) > 3]
        
        print(f"🔍 Query concepts: {query_keywords[:5]}")
        
        with self.driver.session() as session:
            results = []
            
            # Strategy 1: Find chunks that mention query concepts
            if query_keywords:
                cypher_query = """
                    MATCH (m:Mentor {mentor_id: $mentor_id})-[:HAS_DOCUMENT]->(d:Document)
                    MATCH (d)-[:CONTAINS]->(ch:Chunk)-[:MENTIONS]->(c:Concept)
                    WHERE c.name IN $concepts
                    WITH ch, d, COUNT(DISTINCT c) as matches
                    RETURN ch.text as text, 
                           d.name as source,
                           matches,
                           ch.index as chunk_index
                    ORDER BY matches DESC
                    LIMIT $limit
                """
                
                result = session.run(
                    cypher_query,
                    mentor_id=mentor_id,
                    concepts=query_keywords[:10],  # Limit concepts
                    limit=top_k
                )
                
                for record in result:
                    results.append({
                        'text': record['text'],
                        'source': record['source'],
                        'relevance_score': record['matches'],
                        'chunk_index': record['chunk_index']
                    })
            
            # Strategy 2: Fallback to text search if no concept matches
            if not results:
                print("⚠️ No concept matches, trying text search")
                
                # Simple text search in chunks
                text_query = """
                    MATCH (m:Mentor {mentor_id: $mentor_id})-[:HAS_DOCUMENT]->(d:Document)
                    MATCH (d)-[:CONTAINS]->(ch:Chunk)
                    WHERE toLower(ch.text) CONTAINS $query_text
                    RETURN ch.text as text,
                           d.name as source,
                           1 as relevance_score,
                           ch.index as chunk_index
                    LIMIT $limit
                """
                
                result = session.run(
                    text_query,
                    mentor_id=mentor_id,
                    query_text=query.lower(),
                    limit=top_k
                )
                
                for record in result:
                    results.append({
                        'text': record['text'],
                        'source': record['source'],
                        'relevance_score': record['relevance_score'],
                        'chunk_index': record['chunk_index']
                    })
            
            if results:
                print(f"✅ Found {len(results)} relevant chunks from knowledge graph")
            else:
                print(f"⚠️ No relevant chunks found in knowledge graph")
            
            return results
    
    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """Split text into chunks"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            current_chunk.append(word)
            current_size += 1
            
            if current_size >= chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_size = 0
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _query_simple(self, mentor_id: int, query: str, top_k: int) -> List[Dict]:
        """Simple query without NLP (fallback)"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (m:Mentor {mentor_id: $mentor_id})-[:HAS_DOCUMENT]->(d:Document)
                MATCH (d)-[:CONTAINS]->(ch:Chunk)
                WHERE toLower(ch.text) CONTAINS $query
                RETURN ch.text as text, d.name as source
                LIMIT $limit
            """, mentor_id=mentor_id, query=query.lower(), limit=top_k)
            
            return [
                {'text': r['text'], 'source': r['source'], 'relevance_score': 1}
                for r in result
            ]
    
    def _add_document_simple(self, mentor_id: int, document_text: str, document_name: str, chunk_size: int):
        """Fallback: Add document without NLP"""
        with self.driver.session() as session:
            session.run("""
                MATCH (m:Mentor {mentor_id: $mentor_id})
                CREATE (d:Document {name: $name, added_at: datetime()})
                CREATE (m)-[:HAS_DOCUMENT]->(d)
            """, mentor_id=mentor_id, name=document_name)
            
            chunks = self._chunk_text(document_text, chunk_size)
            for i, chunk_text in enumerate(chunks):
                session.run("""
                    MATCH (d:Document {name: $name})
                    CREATE (ch:Chunk {index: $index, text: $text})
                    CREATE (d)-[:CONTAINS]->(ch)
                """, name=document_name, index=i, text=chunk_text)
            
            return len(chunks)
    
    def get_knowledge_summary(self, mentor_id: int) -> Dict:
        """Get summary of mentor's knowledge graph"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (m:Mentor {mentor_id: $mentor_id})
                OPTIONAL MATCH (m)-[:HAS_DOCUMENT]->(d:Document)
                OPTIONAL MATCH (d)-[:CONTAINS]->(ch:Chunk)
                OPTIONAL MATCH (d)-[:MENTIONS]->(c:Concept)
                RETURN 
                    COUNT(DISTINCT d) as documents,
                    COUNT(DISTINCT ch) as chunks,
                    COUNT(DISTINCT c) as concepts
            """, mentor_id=mentor_id)
            
            record = result.single()
            
            return {
                'documents': record['documents'],
                'chunks': record['chunks'],
                'concepts': record['concepts'],
                'status': 'active' if record['documents'] > 0 else 'empty'
            }