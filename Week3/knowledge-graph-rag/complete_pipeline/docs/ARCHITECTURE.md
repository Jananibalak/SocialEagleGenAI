# System Architecture

Complete architectural overview of the Knowledge Graph RAG system.

## Table of Contents

1. [Overview](#overview)
2. [System Components](#system-components)
3. [Data Flow](#data-flow)
4. [Technology Stack](#technology-stack)
5. [Design Patterns](#design-patterns)
6. [Database Schema](#database-schema)
7. [API Architecture](#api-architecture)

---

## Overview

The system implements a **Retrieval-Augmented Generation (RAG)** pipeline using **Knowledge Graphs** for structured context retrieval.

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE GRAPH RAG SYSTEM                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│  INPUT LAYER    │  Documents (TXT, PDF, DOCX, Web)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ EXTRACTION      │  LLM-powered entity/relationship extraction
│    LAYER        │  • Entity recognition
└────────┬────────┘  • Relationship extraction
         │           • Temporal validity capture
         ▼
┌─────────────────┐
│ TRANSFORMATION  │  JSON → Cypher queries
│    LAYER        │  • Validation
└────────┬────────┘  • Deduplication
         │           • Property normalization
         ▼
┌─────────────────┐
│  STORAGE        │  Neo4j Graph Database
│    LAYER        │  • Nodes (entities)
└────────┬────────┘  • Relationships (edges)
         │           • Properties (metadata)
         ▼
┌─────────────────┐
│ RETRIEVAL       │  Graph-based context retrieval
│    LAYER        │  • Entity lookup
└────────┬────────┘  • Multi-hop traversal
         │           • Fuzzy matching
         ▼
┌─────────────────┐
│ GENERATION      │  LLM answer generation
│    LAYER        │  • Context formatting
└────────┬────────┘  • Prompt engineering
         │           • Citation tracking
         ▼
┌─────────────────┐
│  OUTPUT         │  Natural language answers
│    LAYER        │  • Cited facts
└─────────────────┘  • Source tracking
```

---

## System Components

### 1. Configuration Module (`config.py`)

**Purpose:** Centralized configuration management

**Responsibilities:**
- Load environment variables
- Validate configuration
- Provide configuration constants

**Key Functions:**
```python
verify_config()  # Validates all required config
```

**Configuration Sources:**
- `.env` file (development)
- Environment variables (production)

---

### 2. Knowledge Extractor (`extract_knowledge.py`)

**Purpose:** Extract structured knowledge from unstructured text

**Architecture:**
```
Text Input
    ↓
Prompt Engineering
    ↓
LLM API Call (GPT-4o-mini)
    ↓
JSON Response
    ↓
Validation & Parsing
    ↓
Structured Knowledge
```

**Key Components:**
```python
class KnowledgeExtractor:
    __init__()                      # Initialize LLM client
    extract_from_text(text)         # Main extraction method
    _build_extraction_prompt(text)  # Prompt engineering
    _parse_json_response(response)  # Parse LLM output
    _validate_knowledge(knowledge)  # Validate structure
```

**Extraction Schema:**
```json
{
  "entities": [
    {
      "name": "string",
      "type": "Person|Organization|Location|Product",
      "properties": {
        "key": "value"
      }
    }
  ],
  "relationships": [
    {
      "source": "entity_name",
      "target": "entity_name",
      "type": "RELATIONSHIP_TYPE",
      "properties": {
        "valid_from": "YYYY",
        "valid_to": "YYYY|present",
        "description": "string"
      }
    }
  ]
}
```

**Error Handling:**
- JSON parsing errors → retry or skip
- API errors → exponential backoff
- Validation errors → log and continue

---

### 3. Graph Builder (`graph_builder.py`)

**Purpose:** Manage Neo4j graph database operations

**Architecture:**
```
Knowledge JSON
    ↓
Cypher Query Generation
    ↓
Transaction Management
    ↓
Batch Execution
    ↓
Neo4j Graph
```

**Key Components:**
```python
class GraphBuilder:
    __init__(uri, user, password)           # Connect to Neo4j
    create_entity(entity)                   # Create single node
    batch_create_entities(entities)         # Create multiple nodes
    create_relationship(relationship)       # Create single edge
    batch_create_relationships(rels)        # Create multiple edges
    build_from_knowledge(knowledge)         # Complete build
    get_database_stats()                    # Graph statistics
    find_entity(name)                       # Entity lookup
    find_relationships_for_entity(name)     # Relationship lookup
```

**Database Operations:**

1. **Entity Creation**
```cypher
MERGE (e:Person {name: $name})
SET e += $properties
RETURN e
```

2. **Relationship Creation**
```cypher
MATCH (source {name: $source_name})
MATCH (target {name: $target_name})
MERGE (source)-[r:FOUNDED]->(target)
SET r += $properties
RETURN r
```

**Transaction Strategy:**
- Use transactions for batch operations
- MERGE instead of CREATE (idempotent)
- Entities before relationships (dependencies)

---

### 4. Pipeline (`pipeline.py`)

**Purpose:** Orchestrate end-to-end document processing

**Process Flow:**
```
Document File
    ↓
[1] Load Document
    ├─ Read file
    ├─ Handle encoding
    └─ Validate content
    ↓
[2] Chunk Text
    ├─ Split by paragraphs/sentences
    ├─ Preserve context
    └─ Filter empty chunks
    ↓
[3] For Each Chunk
    ├─ Extract knowledge (LLM)
    ├─ Validate extraction
    └─ Track statistics
    ↓
[4] Build Graph
    ├─ Create entities
    ├─ Create relationships
    └─ Handle duplicates
    ↓
[5] Report Statistics
```

**Key Components:**
```python
class KnowledgeGraphPipeline:
    __init__()                              # Initialize components
    load_document(filepath)                 # Load file
    chunk_text(text, method)                # Split text
    process_chunk(chunk, id)                # Extract + validate
    build_graph_from_knowledge(knowledge)   # Store in Neo4j
    process_document(filepath)              # Complete pipeline
    process_multiple_documents(directory)   # Batch processing
    report_statistics()                     # Show results
```

**Chunking Strategies:**

1. **Paragraph-based** (default)
   - Split on `\n\n`
   - Preserves semantic units
   - Best for well-formatted text

2. **Sentence-based**
   - Split on periods
   - Smaller chunks
   - Better for dense text

3. **Fixed-size**
   - Fixed character length with overlap
   - Prevents context loss at boundaries

---

### 5. RAG Query System (`advanced_rag.py`)

**Purpose:** Answer questions using graph context

**Query Flow:**
```
User Question
    ↓
[1] Entity Extraction
    ├─ Extract mentions from question
    └─ Fuzzy match to graph entities
    ↓
[2] Context Retrieval
    ├─ Find entities in graph
    ├─ Traverse relationships (N-hops)
    └─ Format as readable text
    ↓
[3] Answer Generation
    ├─ Build prompt with context
    ├─ Call LLM
    └─ Parse answer
    ↓
Natural Language Answer
```

**Key Components:**
```python
class AdvancedRAGSystem:
    __init__()                                  # Initialize LLM + Graph
    fuzzy_search_entities(term, limit)          # Partial name matching
    extract_entities_with_fuzzy_match(question) # Entity extraction
    retrieve_graph_context(entities, hops)      # Context retrieval
    _format_enhanced_context(entity, rels)      # Format context
    generate_answer(question, context)          # LLM generation
    query(question, hops, show_context)         # Complete query
```

**Fuzzy Matching:**
```cypher
MATCH (e)
WHERE toLower(e.name) CONTAINS toLower($search_term)
RETURN e, 
  CASE 
    WHEN toLower(e.name) = toLower($term) THEN 100
    WHEN toLower(e.name) STARTS WITH toLower($term) THEN 90
    WHEN toLower(e.name) ENDS WITH toLower($term) THEN 80
    ELSE 70
  END as score
ORDER BY score DESC
```

**Multi-hop Traversal:**
```cypher
MATCH (start {name: $entity})
OPTIONAL MATCH path = (start)-[*1..2]-(connected)
RETURN start, collect(DISTINCT connected), relationships(path)
```

---

## Data Flow

### Document to Graph Flow
```
┌──────────────┐
│  Document    │  "Amazon was founded by Jeff Bezos in 1994..."
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Chunking    │  ["Amazon was founded...", "Jeff Bezos served..."]
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Extraction  │  LLM analyzes: "Find entities and relationships"
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  JSON        │  {entities: [{name: "Amazon", type: "Organization"}],
└──────┬───────┘   relationships: [{source: "Jeff Bezos", ...}]}
       │
       ▼
┌──────────────┐
│  Validation  │  Check schema, required fields
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Cypher      │  MERGE (e:Organization {name: "Amazon"})
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Neo4j       │  (Amazon)-[:FOUNDED_BY]->(Jeff Bezos)
└──────────────┘
```

### Query to Answer Flow
```
┌──────────────┐
│  Question    │  "Who founded Amazon?"
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Entity      │  LLM extracts: ["Amazon"]
│  Extraction  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Fuzzy       │  "Amazon" → matches "Amazon" (100% score)
│  Matching    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Graph       │  MATCH (Amazon)-[r]-(connected)
│  Traversal   │  Returns: Jeff Bezos, FOUNDED relationship, 1994
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Context     │  "Entity: Amazon (Organization)
│  Formatting  │   - founded: 1994
└──────┬───────┘    Relationships: Jeff Bezos --[FOUNDED]--> Amazon"
       │
       ▼
┌──────────────┐
│  LLM         │  "Based on the context, Jeff Bezos founded Amazon
│  Generation  │   in 1994..."
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Answer      │  Display to user with citations
└──────────────┘
```

---

## Technology Stack

### Core Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Language** | Python 3.8+ | Main programming language |
| **LLM API** | OpenRouter + GPT-4o-mini | Entity extraction & answer generation |
| **Graph DB** | Neo4j 5.x | Knowledge graph storage |
| **LLM Framework** | OpenAI SDK | API client |
| **Environment** | python-dotenv | Configuration management |

### Dependencies
```
openai==2.16.0          # LLM API client
neo4j==6.1.0            # Neo4j driver
python-dotenv==1.2.1    # Environment variables
langchain==1.2.8        # (optional) LLM framework
langchain-community     # (optional) Community integrations
```

### Infrastructure

- **Development**: Docker Desktop (Neo4j container)
- **Production**: Neo4j Aura / Self-hosted Neo4j cluster

---

## Design Patterns

### 1. Pipeline Pattern

**Used in:** `pipeline.py`

**Purpose:** Break complex process into stages
```
Load → Chunk → Extract → Validate → Store → Report
```

**Benefits:**
- Each stage is testable
- Easy to add new stages
- Clear error handling per stage

### 2. Repository Pattern

**Used in:** `graph_builder.py`

**Purpose:** Abstract database operations
```python
class GraphBuilder:
    # Hides Cypher details
    # Provides high-level interface
    def create_entity(entity)
    def find_entity(name)
```

**Benefits:**
- Easy to swap databases
- Simplified testing
- Consistent interface

### 3. Strategy Pattern

**Used in:** Chunking methods

**Purpose:** Swap algorithms at runtime
```python
chunking_method = "paragraph"  # or "sentence" or "fixed_size"
chunks = pipeline.chunk_text(text, method=chunking_method)
```

**Benefits:**
- Flexible chunking strategies
- Easy to add new strategies
- Runtime configuration

### 4. Factory Pattern

**Used in:** LLM client initialization

**Purpose:** Create objects without specifying exact class
```python
client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=API_KEY)
# Could swap to Anthropic, Cohere, etc.
```

---

## Database Schema

### Node Types (Labels)
```cypher
(:Person {name, type, properties...})
(:Organization {name, type, properties...})
(:Location {name, type, properties...})
(:Product {name, type, properties...})
```

### Relationship Types
```cypher
-[:FOUNDED {valid_from, valid_to, description}]->
-[:CEO_OF {valid_from, valid_to, description}]->
-[:WORKS_AT {valid_from, valid_to, since}]->
-[:LOCATED_IN {valid_from, valid_to}]->
-[:LED {valid_from, valid_to}]->
```

### Example Graph
```
(Jeff Bezos:Person {name: "Jeff Bezos", role: "Founder"})
    |
    | -[:FOUNDED {valid_from: "1994"}]->
    |
    v
(Amazon:Organization {name: "Amazon", founded: 1994})
    |
    | -[:LOCATED_IN {valid_from: "1994", valid_to: "present"}]->
    |
    v
(Seattle:Location {name: "Seattle", state: "Washington"})

(Andy Jassy:Person {name: "Andy Jassy"})
    |
    | -[:CEO_OF {valid_from: "2021", valid_to: "present"}]->
    |
    v
(Amazon)
```

### Indexes
```cypher
-- For performance
CREATE INDEX entity_name FOR (e:Person) ON (e.name);
CREATE INDEX org_name FOR (e:Organization) ON (e.name);
CREATE INDEX location_name FOR (e:Location) ON (e.name);
```

---

## API Architecture

### Internal API Structure
```python
# Configuration Layer
config.verify_config()
→ Validates environment

# Extraction Layer
extractor = KnowledgeExtractor()
knowledge = extractor.extract_from_text(text)
→ Returns JSON

# Storage Layer
builder = GraphBuilder(uri, user, pass)
builder.build_from_knowledge(knowledge)
→ Stores in Neo4j

# Query Layer
rag = AdvancedRAGSystem()
response = rag.query(question)
→ Returns answer
```

### Future REST API
```python
# FastAPI structure (not implemented yet)
from fastapi import FastAPI

app = FastAPI()

@app.post("/api/v1/documents")
def upload_document(file: UploadFile):
    """Process and index document"""
    pass

@app.get("/api/v1/query")
def query_graph(question: str, hops: int = 2):
    """Answer question using graph"""
    pass

@app.get("/api/v1/entities/search")
def search_entities(term: str):
    """Fuzzy search entities"""
    pass
```

---

## Performance Considerations

### Bottlenecks

1. **LLM API Calls**
   - Slowest part (~2-5s per chunk)
   - Rate limited by API provider
   - Solution: Batch requests, cache results

2. **Graph Traversal**
   - Multi-hop queries can be slow on large graphs
   - Solution: Limit hops, add indexes

3. **Document Processing**
   - Large documents take time
   - Solution: Parallel processing, streaming

### Optimization Strategies

1. **Caching**
```python
# Cache frequent queries
@lru_cache(maxsize=1000)
def retrieve_context(entity_name):
    pass
```

2. **Batching**
```python
# Process multiple chunks in one API call
batch_extract(chunks)  # Instead of loop
```

3. **Indexing**
```cypher
-- Add indexes for common queries
CREATE INDEX ON :Person(name)
```

---

## Security Considerations

### 1. API Key Management
- Never commit `.env` to version control
- Use secrets management in production
- Rotate keys regularly

### 2. Input Validation
- Validate file types before processing
- Limit file sizes
- Sanitize user queries

### 3. Database Access
- Use parameterized queries (prevent injection)
- Limit query complexity
- Implement authentication

### 4. Rate Limiting
```python
# Limit queries per user
from ratelimit import limits

@limits(calls=10, period=60)
def query(question):
    pass
```

---

## Scalability

### Horizontal Scaling
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Worker 1   │     │  Worker 2   │     │  Worker 3   │
│  (Extract)  │     │  (Extract)  │     │  (Extract)  │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┴───────────────────┘
                           │
                           ▼
                   ┌───────────────┐
                   │    Neo4j      │
                   │   Cluster     │
                   └───────────────┘
```

### Vertical Scaling

- Increase Neo4j memory allocation
- Use faster storage (SSD)
- Optimize query patterns

---

## Monitoring & Logging

### Key Metrics

1. **Extraction Metrics**
   - Entities extracted per document
   - Relationships extracted per document
   - Extraction failures
   - API latency

2. **Graph Metrics**
   - Total nodes
   - Total relationships
   - Query latency
   - Storage size

3. **Query Metrics**
   - Questions per minute
   - Average response time
   - Cache hit rate
   - Error rate

### Logging Strategy
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kg_rag.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("Processing document: %s", filename)
```

---

**Next:** See [API_REFERENCE.md](API_REFERENCE.md) for detailed code documentation.