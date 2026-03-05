import os
from typing import List, Dict
from pathlib import Path

from config import verify_config, NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from extract_knowledge import KnowledgeExtractor
from graph_builder import GraphBuilder

# ============================================================================
# KNOWLEDGE GRAPH PIPELINE
# ============================================================================

class KnowledgeGraphPipeline:
    """
    End-to-end pipeline for building knowledge graphs from documents
    
    Pipeline Stages:
    1. Document Loading (read files)
    2. Text Chunking (split into processable pieces)
    3. Knowledge Extraction (LLM analysis)
    4. Graph Building (store in Neo4j)
    5. Validation (ensure quality)
    
    Design Pattern: Pipeline Pattern
    - Each stage can be tested independently
    - Easy to add new stages
    - Clear data flow
    
    Why this architecture?
    - Separation of Concerns: Each component has one job
    - Testability: Mock any stage for testing
    - Flexibility: Easy to swap components (different LLMs, databases)
    - Scalability: Can parallelize stages
    """
    
    def __init__(self):
        """
        Initialize pipeline components
        
        Process:
        1. Verify configuration
        2. Initialize extractor (LLM connection)
        3. Initialize graph builder (Neo4j connection)
        4. Set up tracking variables
        """
        print("="*70)
        print("INITIALIZING KNOWLEDGE GRAPH PIPELINE")
        print("="*70)
        
        # Verify configuration
        verify_config()
        
        # Initialize components
        self.extractor = KnowledgeExtractor()
        self.graph_builder = GraphBuilder(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
        
        # Pipeline statistics
        self.stats = {
            "documents_processed": 0,
            "chunks_processed": 0,
            "entities_created": 0,
            "relationships_created": 0,
            "errors": []
        }
        
        print("✓ Pipeline initialized\n")
    
    def close(self):
        """
        Clean up resources
        
        Best Practice: Always close connections
        - Prevents resource leaks
        - Ensures all writes are flushed
        """
        self.graph_builder.close()
        print("✓ Pipeline closed")
    
    # ========================================================================
    # DOCUMENT LOADING
    # ========================================================================
    
    def load_document(self, filepath: str) -> str:
        """
        Load document from file
        
        Supports:
        - .txt files (plain text)
        - Can be extended for .pdf, .docx, .md
        
        Args:
            filepath: Path to document
        
        Returns:
            Document text content
        
        Error Handling:
        - File not found → raise clear error
        - Encoding issues → try multiple encodings
        - Empty file → return empty string with warning
        
        Future Extensions:
        - PDF: Use PyPDF2 or pdfplumber
        - DOCX: Use python-docx
        - HTML: Use BeautifulSoup
        - Markdown: Already text, just load
        """
        try:
            # Check file exists
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Document not found: {filepath}")
            
            # Try UTF-8 first (most common)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read()
            except UnicodeDecodeError:
                # Fallback to latin-1 (handles most files)
                with open(filepath, 'r', encoding='latin-1') as f:
                    text = f.read()
            
            # Validate content
            if not text.strip():
                print(f"⚠ Warning: Document is empty: {filepath}")
                return ""
            
            print(f"✓ Loaded document: {filepath} ({len(text)} characters)")
            self.stats["documents_processed"] += 1
            
            return text
            
        except Exception as e:
            error_msg = f"Error loading document {filepath}: {e}"
            print(f"✗ {error_msg}")
            self.stats["errors"].append(error_msg)
            raise
    
    # ========================================================================
    # TEXT CHUNKING
    # ========================================================================
    
    def chunk_text(self, text: str, method: str = "paragraph") -> List[str]:
        """
        Split text into processable chunks
        
        Why chunk?
        1. LLM context limits (can't process entire book at once)
        2. Better extraction quality (focused analysis)
        3. Parallel processing (can process chunks simultaneously)
        4. Cost efficiency (smaller inputs = lower API costs)
        
        Chunking Strategies:
        
        1. PARAGRAPH-BASED (default):
           - Split on double newlines
           - Preserves semantic units
           - Best for well-formatted text
           - Example: Split blog posts by paragraph
        
        2. SENTENCE-BASED:
           - Split on periods
           - Smaller chunks
           - Better for dense text
           - Example: Academic papers
        
        3. SLIDING WINDOW:
           - Overlapping chunks
           - Captures context across boundaries
           - Example: "chunk1: [0:500]", "chunk2: [400:900]"
           - Prevents missing relationships that span boundaries
        
        4. SEMANTIC CHUNKING (advanced):
           - Split based on topic changes
           - Use embeddings to detect topic shifts
           - Most sophisticated but computationally expensive
        
        Args:
            text: Full document text
            method: Chunking strategy
        
        Returns:
            List of text chunks
        
        Best Practices:
        - Chunk size: 500-2000 characters (balances context and cost)
        - Preserve sentences (don't cut mid-sentence)
        - Add overlap for context continuity
        - Filter empty chunks
        """
        if method == "paragraph":
            # Split on double newlines (paragraphs)
            chunks = [chunk.strip() for chunk in text.split("\n\n")]
            
        elif method == "sentence":
            # Simple sentence splitting (can be improved with NLTK)
            import re
            sentences = re.split(r'(?<=[.!?])\s+', text)
            
            # Group sentences into chunks of ~3 sentences
            chunks = []
            current_chunk = []
            
            for sentence in sentences:
                current_chunk.append(sentence)
                if len(current_chunk) >= 3:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
            
            # Add remaining sentences
            if current_chunk:
                chunks.append(" ".join(current_chunk))
        
        elif method == "fixed_size":
            # Fixed character length with overlap
            chunk_size = 1000
            overlap = 200
            chunks = []
            
            start = 0
            while start < len(text):
                end = start + chunk_size
                chunk = text[start:end]
                
                # Try to end at sentence boundary
                if end < len(text):
                    last_period = chunk.rfind('.')
                    if last_period > chunk_size * 0.7:  # At least 70% of chunk
                        chunk = chunk[:last_period + 1]
                        end = start + last_period + 1
                
                chunks.append(chunk.strip())
                start = end - overlap  # Overlap for context
        
        else:
            raise ValueError(f"Unknown chunking method: {method}")
        
        # Filter empty chunks
        chunks = [c for c in chunks if c.strip()]
        
        print(f"✓ Split into {len(chunks)} chunks using '{method}' method")
        
        return chunks
    
    # ========================================================================
    # KNOWLEDGE EXTRACTION FROM CHUNKS
    # ========================================================================
    
    def process_chunk(self, chunk: str, chunk_id: int) -> Dict:
        """
        Extract knowledge from a single chunk
        
        Process:
        1. Send chunk to LLM for extraction
        2. Validate extracted knowledge
        3. Track statistics
        4. Handle errors gracefully
        
        Args:
            chunk: Text chunk to process
            chunk_id: Identifier for tracking
        
        Returns:
            Extracted knowledge or None if failed
        
        Error Handling Strategy:
        - Network errors → retry with exponential backoff
        - Parsing errors → log and skip chunk
        - Rate limits → wait and retry
        - Continue processing other chunks even if one fails
        """
        print(f"\n{'─'*70}")
        print(f"Processing Chunk {chunk_id}")
        print(f"{'─'*70}")
        print(f"Preview: {chunk[:150]}...")
        
        try:
            # Extract knowledge using LLM
            knowledge = self.extractor.extract_from_text(chunk)
            
            if knowledge:
                # Track statistics
                entity_count = len(knowledge.get("entities", []))
                relationship_count = len(knowledge.get("relationships", []))
                
                print(f"✓ Extracted: {entity_count} entities, {relationship_count} relationships")
                
                self.stats["chunks_processed"] += 1
                
                return knowledge
            else:
                error_msg = f"Failed to extract knowledge from chunk {chunk_id}"
                print(f"✗ {error_msg}")
                self.stats["errors"].append(error_msg)
                return None
                
        except Exception as e:
            error_msg = f"Error processing chunk {chunk_id}: {e}"
            print(f"✗ {error_msg}")
            self.stats["errors"].append(error_msg)
            return None
    
    # ========================================================================
    # GRAPH BUILDING FROM EXTRACTED KNOWLEDGE
    # ========================================================================
    
    def build_graph_from_knowledge(self, knowledge: Dict):
        """
        Store extracted knowledge in Neo4j
        
        Process:
        1. Create all entities first
        2. Then create relationships
        3. Track statistics
        
        Why this order?
        - Relationships need both endpoints to exist
        - Neo4j will error if target node doesn't exist
        
        Deduplication:
        - MERGE ensures no duplicate entities
        - Multiple extractions of "Amazon" → single node
        - Properties are updated with latest values
        
        Args:
            knowledge: Extracted entities and relationships
        """
        try:
            stats = self.graph_builder.build_from_knowledge(knowledge)
            
            # Update pipeline statistics
            self.stats["entities_created"] += stats["entities_created"]
            self.stats["relationships_created"] += stats["relationships_created"]
            
        except Exception as e:
            error_msg = f"Error building graph: {e}"
            print(f"✗ {error_msg}")
            self.stats["errors"].append(error_msg)
    
    # ========================================================================
    # MAIN PIPELINE EXECUTION
    # ========================================================================
    
    def process_document(
        self, 
        filepath: str, 
        chunking_method: str = "paragraph",
        clear_graph: bool = False
    ):
        """
        Complete pipeline: Document → Knowledge Graph
        
        Pipeline Flow:
        
        Document File
            ↓
        [1] Load Document
            ↓
        Full Text
            ↓
        [2] Chunk Text
            ↓
        Text Chunks
            ↓
        [3] For Each Chunk:
            ├─ Extract Entities
            ├─ Extract Relationships
            └─ Validate JSON
            ↓
        Knowledge Objects
            ↓
        [4] Build Graph:
            ├─ Create Entity Nodes
            ├─ Create Relationships
            └─ Handle Duplicates
            ↓
        Knowledge Graph in Neo4j
        
        Args:
            filepath: Path to document
            chunking_method: How to split text
            clear_graph: Whether to clear existing graph first
        
        Process:
        1. Optionally clear existing graph
        2. Load document
        3. Chunk text
        4. Process each chunk
        5. Build graph
        6. Report statistics
        
        Production Considerations:
        - Add retry logic for API failures
        - Implement rate limiting
        - Add progress bars for long documents
        - Save checkpoints for resumability
        - Parallel processing for multiple chunks
        """
        print("\n" + "="*70)
        print(f"PROCESSING DOCUMENT: {filepath}")
        print("="*70)
        
        # Step 0: Clear graph if requested
        if clear_graph:
            print("\n[Step 0] Clearing existing graph...")
            self.graph_builder.clear_database()
        
        # Step 1: Load document
        print("\n[Step 1] Loading document...")
        text = self.load_document(filepath)
        
        if not text:
            print("✗ No text to process")
            return
        
        # Step 2: Chunk text
        print("\n[Step 2] Chunking text...")
        chunks = self.chunk_text(text, method=chunking_method)
        
        if not chunks:
            print("✗ No chunks created")
            return
        
        print(f"\n[Step 3] Processing {len(chunks)} chunks...")
        
        # Step 3 & 4: Process each chunk and build graph
        for i, chunk in enumerate(chunks, 1):
            # Extract knowledge
            knowledge = self.process_chunk(chunk, i)
            
            if knowledge:
                # Build graph from this chunk's knowledge
                self.build_graph_from_knowledge(knowledge)
        
        # Step 5: Report results
        self.report_statistics()
    
    def process_multiple_documents(
        self, 
        directory: str, 
        file_pattern: str = "*.txt",
        chunking_method: str = "paragraph",
        clear_graph: bool = False
    ):
        """
        Process all documents in a directory
        
        Use Case: Build knowledge graph from document collection
        Example: Process all company reports, research papers, etc.
        
        Args:
            directory: Path to directory
            file_pattern: Glob pattern for files (e.g., "*.txt", "*.pdf")
            chunking_method: How to chunk text
            clear_graph: Clear graph before starting
        
        Process:
        1. Find all matching files
        2. Clear graph once (not per document)
        3. Process each document
        4. Accumulate statistics
        
        Production Enhancement:
        - Add file prioritization
        - Implement resume from checkpoint
        - Add progress tracking
        - Parallel document processing
        """
        # Find all matching files
        path = Path(directory)
        files = list(path.glob(file_pattern))
        
        if not files:
            print(f"✗ No files matching '{file_pattern}' found in {directory}")
            return
        
        print(f"\nFound {len(files)} documents to process")
        
        # Clear graph once if requested
        if clear_graph:
            self.graph_builder.clear_database()
        
        # Process each document
        for i, filepath in enumerate(files, 1):
            print(f"\n{'='*70}")
            print(f"Document {i}/{len(files)}: {filepath.name}")
            print(f"{'='*70}")
            
            self.process_document(
                str(filepath), 
                chunking_method=chunking_method,
                clear_graph=False  # Already cleared once
            )
        
        # Final report
        print("\n" + "="*70)
        print("ALL DOCUMENTS PROCESSED")
        print("="*70)
        self.report_statistics()
    
    # ========================================================================
    # STATISTICS AND REPORTING
    # ========================================================================
    
    def report_statistics(self):
        """
        Display pipeline statistics
        
        Shows:
        - Documents processed
        - Chunks processed
        - Entities created
        - Relationships created
        - Errors encountered
        - Graph database state
        
        Use Case:
        - Monitor pipeline progress
        - Debug issues
        - Validate results
        """
        print("\n" + "="*70)
        print("PIPELINE STATISTICS")
        print("="*70)
        
        print(f"\nProcessing:")
        print(f"  Documents processed:   {self.stats['documents_processed']}")
        print(f"  Chunks processed:      {self.stats['chunks_processed']}")
        
        print(f"\nGraph Building:")
        print(f"  Entities created:      {self.stats['entities_created']}")
        print(f"  Relationships created: {self.stats['relationships_created']}")
        
        if self.stats["errors"]:
            print(f"\nErrors ({len(self.stats['errors'])}):")
            for error in self.stats["errors"]:
                print(f"  ✗ {error}")
        else:
            print(f"\n✓ No errors encountered")
        
        # Get current graph state
        db_stats = self.graph_builder.get_database_stats()
        
        print(f"\nGraph Database State:")
        print(f"  Total nodes:           {db_stats['nodes']}")
        print(f"  Total relationships:   {db_stats['relationships']}")
        print(f"  Node labels:           {', '.join(db_stats['labels'])}")
        print(f"  Relationship types:    {', '.join(db_stats['relationship_types'])}")
        
        print("\n" + "="*70)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main entry point for the pipeline
    
    Usage Examples:
    
    1. Process single document:
       python pipeline.py
    
    2. Process directory of documents:
       Modify main() to use process_multiple_documents()
    
    3. Custom chunking:
       Change chunking_method parameter
    """
    
    # Initialize pipeline
    pipeline = KnowledgeGraphPipeline()
    
    try:
        # Example 1: Process single document
        pipeline.process_document(
            filepath="knowledge_base.txt",
            chunking_method="paragraph",  # Options: paragraph, sentence, fixed_size
            clear_graph=True  # Clear existing graph first
        )
        
        # Example 2: Process multiple documents (commented out)
        # pipeline.process_multiple_documents(
        #     directory="./documents",
        #     file_pattern="*.txt",
        #     chunking_method="paragraph",
        #     clear_graph=True
        # )
        
        # Visualization instructions
        print("\n" + "="*70)
        print("✓ PIPELINE COMPLETED SUCCESSFULLY")
        print("="*70)
        print("\nVisualize your knowledge graph:")
        print("1. Open Neo4j Browser: http://localhost:7474/browser/")
        print("2. Run query: MATCH (n) RETURN n LIMIT 50")
        print("\nExplore relationships:")
        print("3. Run query: MATCH (p:Person)-[r]->(o) RETURN p, r, o")
        print("4. Run query: MATCH path = (n)-[*1..2]-(m) RETURN path LIMIT 25")
        
    finally:
        # Always close connections
        pipeline.close()


if __name__ == "__main__":
    main()