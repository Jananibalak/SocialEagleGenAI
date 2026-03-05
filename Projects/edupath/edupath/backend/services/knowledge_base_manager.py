from typing import List, Dict
import chromadb
from sentence_transformers import SentenceTransformer
import os
from pathlib import Path

class KnowledgeBaseManager:
    """Manage vector embeddings for RAG"""
    
    def __init__(self):
        # Initialize ChromaDB
        self.chroma_path = Path("data/chromadb")
        self.chroma_path.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=str(self.chroma_path))
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def create_mentor_collection(self, mentor_id: int):
        """Create a new collection for a mentor's knowledge base"""
        collection_name = f"mentor_{mentor_id}"
        
        try:
            # Delete if exists (for fresh start)
            try:
                self.client.delete_collection(collection_name)
            except:
                pass
            
            # Create new collection
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"mentor_id": mentor_id}
            )
            
            return collection
        except Exception as e:
            print(f"Error creating collection: {e}")
            return None
    
    def add_document_to_knowledge_base(
        self,
        mentor_id: int,
        document_text: str,
        document_name: str,
        chunk_size: int = 500
    ):
        """
        Add document to mentor's knowledge base with chunking
        
        Args:
            mentor_id: ID of the mentor
            document_text: Full text of document
            document_name: Name of the document
            chunk_size: Size of text chunks (tokens)
        """
        collection_name = f"mentor_{mentor_id}"
        
        try:
            collection = self.client.get_or_create_collection(collection_name)
        except:
            collection = self.create_mentor_collection(mentor_id)
        
        # Chunk the document
        chunks = self._chunk_text(document_text, chunk_size)
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(chunks).tolist()
        
        # Create IDs
        ids = [f"{document_name}_{i}" for i in range(len(chunks))]
        
        # Metadata
        metadatas = [
            {
                'source': document_name,
                'chunk_index': i,
                'total_chunks': len(chunks)
            }
            for i in range(len(chunks))
        ]
        
        # Add to collection
        collection.add(
            embeddings=embeddings,
            documents=chunks,
            ids=ids,
            metadatas=metadatas
        )
        
        print(f"✅ Added {len(chunks)} chunks from '{document_name}' to mentor {mentor_id}'s knowledge base")
        
        return len(chunks)
    
    def query_knowledge_base(
        self,
        mentor_id: int,
        query: str,
        top_k: int = 3
    ) -> List[Dict]:
        """
        Query mentor's knowledge base for relevant context
        
        Returns:
            List of relevant text chunks with metadata
        """
        collection_name = f"mentor_{mentor_id}"
        
        try:
            collection = self.client.get_collection(collection_name)
        except:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        # Search
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )
        
        # Format results
        context_chunks = []
        if results['documents']:
            for i in range(len(results['documents'][0])):
                context_chunks.append({
                    'text': results['documents'][0][i],
                    'source': results['metadatas'][0][i].get('source', 'unknown'),
                    'distance': results['distances'][0][i] if 'distances' in results else 0
                })
        
        return context_chunks
    
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
    
    def get_knowledge_summary(self, mentor_id: int) -> Dict:
        """Get summary of mentor's knowledge base"""
        collection_name = f"mentor_{mentor_id}"
        
        try:
            collection = self.client.get_collection(collection_name)
            count = collection.count()
            
            return {
                'total_chunks': count,
                'status': 'active' if count > 0 else 'empty'
            }
        except:
            return {
                'total_chunks': 0,
                'status': 'not_created'
            }