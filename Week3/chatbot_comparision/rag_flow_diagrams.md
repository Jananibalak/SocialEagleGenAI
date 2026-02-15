# RAG Chatbot - Visual Flow Diagrams

## 📊 Overall System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        RAG CHATBOT SYSTEM                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐       ┌──────────────────┐      ┌─────────────┐
│   USER UPLOADS  │       │  DOCUMENT        │      │   CHUNKING  │
│   - PDF File    │──────▶│  PROCESSING      │─────▶│   - Split   │
│   - URL/Web     │       │  - Extract Text  │      │   - Overlap │
└─────────────────┘       └──────────────────┘      └─────────────┘
                                                            │
                                                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EMBEDDING GENERATION                         │
│  "Machine learning is..."  →  [0.2, 0.8, -0.3, 0.5, ...]      │
│         (Text)                      (Vector/Numbers)            │
└─────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
        ┌──────────────┐  ┌─────────────┐  ┌──────────────┐
        │  VECTOR DB   │  │  KNOWLEDGE  │  │   AGENTIC    │
        │   (FAISS)    │  │    GRAPH    │  │     RAG      │
        │              │  │   (Neo4j)   │  │ (+ Web Tool) │
        └──────────────┘  └─────────────┘  └──────────────┘
                    │               │               │
                    └───────────────┼───────────────┘
                                    │
                                    ▼
                        ┌───────────────────┐
                        │  USER QUESTION    │
                        │ "What is ML?"     │
                        └───────────────────┘
                                    │
                                    ▼
                        ┌───────────────────┐
                        │  RETRIEVE TOP     │
                        │  RELEVANT CHUNKS  │
                        └───────────────────┘
                                    │
                                    ▼
                        ┌───────────────────┐
                        │  SEND TO LLM      │
                        │  Context +        │
                        │  Question         │
                        └───────────────────┘
                                    │
                                    ▼
                        ┌───────────────────┐
                        │  GENERATE ANSWER  │
                        │  "ML is a subset  │
                        │  of AI that..."   │
                        └───────────────────┘
                                    │
                                    ▼
                        ┌───────────────────┐
                        │  DISPLAY TO USER  │
                        └───────────────────┘
```

---

## 🔄 Detailed Query Flow - Vector DB RAG

```
Step 1: USER ASKS QUESTION
┌─────────────────────────────────┐
│ "What is machine learning?"    │
└─────────────────────────────────┘
                │
                ▼
Step 2: CONVERT QUESTION TO VECTOR
┌─────────────────────────────────┐
│ OpenAI Embeddings API           │
│ Text → [0.12, 0.89, -0.34, ...] │
└─────────────────────────────────┘
                │
                ▼
Step 3: SEARCH VECTOR DATABASE (FAISS)
┌───────────────────────────────────────────┐
│  Compare question vector with all         │
│  document vectors using cosine similarity │
│                                            │
│  Question: [0.12, 0.89, -0.34, ...]       │
│  Doc 1:    [0.15, 0.87, -0.30, ...]  ✓    │
│  Doc 2:    [0.90, 0.10, 0.50, ...]        │
│  Doc 3:    [0.13, 0.88, -0.32, ...]  ✓    │
│  ...                                       │
│                                            │
│  Returns top 3 most similar docs          │
└───────────────────────────────────────────┘
                │
                ▼
Step 4: RETRIEVE CHUNKS
┌──────────────────────────────────────────┐
│ Chunk 1: "Machine learning is a subset  │
│           of artificial intelligence..." │
│                                           │
│ Chunk 2: "ML algorithms learn from data │
│           without explicit programming"  │
│                                           │
│ Chunk 3: "Common ML techniques include   │
│           supervised, unsupervised..."   │
└──────────────────────────────────────────┘
                │
                ▼
Step 5: CREATE PROMPT
┌──────────────────────────────────────────┐
│ Answer based on this context:            │
│                                           │
│ Context:                                  │
│ [Chunk 1 + Chunk 2 + Chunk 3]           │
│                                           │
│ Question: What is machine learning?      │
│                                           │
│ Answer:                                   │
└──────────────────────────────────────────┘
                │
                ▼
Step 6: SEND TO OPENAI GPT
┌──────────────────────────────────────────┐
│  GPT-4 processes:                        │
│  - Reads the context                     │
│  - Understands the question              │
│  - Formulates answer from context        │
└──────────────────────────────────────────┘
                │
                ▼
Step 7: RETURN ANSWER
┌──────────────────────────────────────────┐
│ "Based on the provided documents,       │
│  machine learning is a subset of AI      │
│  where algorithms learn from data        │
│  without explicit programming. Common    │
│  techniques include supervised and       │
│  unsupervised learning."                 │
│                                           │
│ Sources: 3 document chunks               │
└──────────────────────────────────────────┘
```

---

## 🕸️ Knowledge Graph RAG - Detailed Flow

```
Step 1: DOCUMENT PROCESSING
┌──────────────────────────────────────────────────┐
│ Original Text:                                   │
│ "Elon Musk founded SpaceX in 2002. SpaceX      │
│  develops rockets for space exploration."        │
└──────────────────────────────────────────────────┘
                │
                ▼
Step 2: ENTITY EXTRACTION (Using LLM)
┌──────────────────────────────────────────────────┐
│ Prompt to GPT:                                   │
│ "Extract entities and relationships from this    │
│  text: [document text]"                          │
│                                                   │
│ GPT Response:                                    │
│ - Entities: Elon Musk, SpaceX, 2002, rockets    │
│ - Relationships:                                 │
│   (Elon Musk, FOUNDED, SpaceX)                  │
│   (SpaceX, FOUNDED_IN, 2002)                    │
│   (SpaceX, DEVELOPS, rockets)                   │
└──────────────────────────────────────────────────┘
                │
                ▼
Step 3: STORE IN NEO4J GRAPH
┌──────────────────────────────────────────────────┐
│          [Elon Musk]                             │
│               │                                   │
│               │ FOUNDED                          │
│               ▼                                   │
│           [SpaceX] ──FOUNDED_IN──▶ [2002]       │
│               │                                   │
│               │ DEVELOPS                         │
│               ▼                                   │
│           [rockets]                              │
└──────────────────────────────────────────────────┘
                │
                ▼
Step 4: USER QUERY
┌──────────────────────────────────────────────────┐
│ "What company did Elon Musk found?"             │
└──────────────────────────────────────────────────┘
                │
                ▼
Step 5: EXTRACT ENTITIES FROM QUESTION
┌──────────────────────────────────────────────────┐
│ Key entity: "Elon Musk"                          │
│ Relationship: "found" (FOUNDED)                  │
└──────────────────────────────────────────────────┘
                │
                ▼
Step 6: QUERY NEO4J GRAPH
┌──────────────────────────────────────────────────┐
│ Cypher Query:                                    │
│ MATCH (person {name: "Elon Musk"})-[FOUNDED]->(company)
│ RETURN company                                   │
│                                                   │
│ Result: SpaceX                                   │
└──────────────────────────────────────────────────┘
                │
                ▼
Step 7: GENERATE ANSWER
┌──────────────────────────────────────────────────┐
│ "Elon Musk founded SpaceX."                     │
│ Source: Knowledge Graph                          │
└──────────────────────────────────────────────────┘
```

---

## 🤖 Agentic RAG - Decision Flow

```
USER QUESTION: "What is the current price of Tesla stock?"
                │
                ▼
┌──────────────────────────────────────────────────┐
│ STEP 1: SEARCH DOCUMENTS                         │
│ Query vector store for relevant chunks           │
└──────────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────┐
│ STEP 2: CHECK RELEVANCE                          │
│ Prompt: "Does this context answer the question?" │
│                                                   │
│ Context: [Retrieved chunks about Tesla history]  │
│ Question: "Current stock price?"                 │
│                                                   │
│ LLM Response: "NO - context is about history,    │
│                not current stock price"          │
└──────────────────────────────────────────────────┘
                │
                ▼
        ┌───────┴───────┐
        │               │
    YES │               │ NO
        ▼               ▼
┌──────────────┐  ┌──────────────┐
│ Use Document │  │ Use Web      │
│ Context      │  │ Search       │
└──────────────┘  └──────────────┘
                        │
                        ▼
                ┌──────────────────────────────┐
                │ SERPAPI Web Search            │
                │ Query: "Tesla stock price"    │
                │                               │
                │ Result: "$XXX.XX as of..."   │
                └──────────────────────────────┘
                        │
                        ▼
                ┌──────────────────────────────┐
                │ GENERATE ANSWER               │
                │ "Tesla stock is currently     │
                │  trading at $XXX.XX"         │
                │                               │
                │ Source: Web Search            │
                └──────────────────────────────┘
```

---

## 🔍 Vector Similarity Search - How It Works

```
QUESTION: "What is deep learning?"
   │
   ▼ Convert to vector
[0.8, 0.2, 0.9, 0.1, 0.7]
   │
   ▼ Compare with all document vectors

┌─────────────────────────────────────────────────────────┐
│ Document Chunk 1: "Deep learning uses neural networks" │
│ Vector: [0.7, 0.3, 0.8, 0.2, 0.6]                     │
│ Similarity: 0.95 (Very similar!) ✓                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Document Chunk 2: "Cats are small mammals"             │
│ Vector: [0.1, 0.9, 0.2, 0.8, 0.3]                     │
│ Similarity: 0.12 (Not similar)                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Document Chunk 3: "Neural networks mimic brain"        │
│ Vector: [0.75, 0.25, 0.85, 0.15, 0.65]                │
│ Similarity: 0.93 (Very similar!) ✓                     │
└─────────────────────────────────────────────────────────┘

Return top 2 chunks: Chunk 1 and Chunk 3
```

**Cosine Similarity Formula:**
```
similarity = dot_product(vec1, vec2) / (|vec1| * |vec2|)

Ranges from -1 to 1:
  1.0 = Identical
  0.0 = Unrelated
 -1.0 = Opposite
```

---

## 📦 Document Chunking - Visual Example

```
ORIGINAL DOCUMENT (Too large for AI context):
┌───────────────────────────────────────────────────────┐
│ Machine learning is a subset of artificial            │
│ intelligence that enables systems to learn and        │
│ improve from experience without being explicitly      │
│ programmed. The process involves feeding data into    │
│ algorithms that identify patterns and make decisions. │
│ Common types include supervised learning,             │
│ unsupervised learning, and reinforcement learning.    │
│ Applications range from recommendation systems to     │
│ autonomous vehicles.                                  │
└───────────────────────────────────────────────────────┘

                        ▼ SPLIT ▼

CHUNK 1 (1000 chars, starting from beginning):
┌───────────────────────────────────────────────────────┐
│ Machine learning is a subset of artificial            │
│ intelligence that enables systems to learn and        │
│ improve from experience without being explicitly      │
│ programmed. The process involves feeding data into    │
│ algorithms that identify patterns and make decisions. │
└───────────────────────────────────────────────────────┘

CHUNK 2 (1000 chars, with 200 char overlap):
┌───────────────────────────────────────────────────────┐
│ ...algorithms that identify patterns and make         │  ← Overlap
│ decisions. Common types include supervised learning,  │  ← Overlap
│ unsupervised learning, and reinforcement learning.    │
│ Applications range from recommendation systems to     │
│ autonomous vehicles.                                  │
└───────────────────────────────────────────────────────┘

WHY OVERLAP?
- Prevents breaking sentences mid-thought
- Ensures context isn't lost at boundaries
- Improves retrieval quality
```

---

## 🎯 Session State - Memory Management

```
SESSION STATE = APP'S MEMORY
┌──────────────────────────────────────────────────────┐
│  st.session_state = {                                │
│      'messages': [                                   │
│          {                                           │
│              'role': 'user',                         │
│              'content': 'What is ML?',               │
│              'timestamp': '10:30 AM'                 │
│          },                                          │
│          {                                           │
│              'role': 'assistant',                    │
│              'content': 'ML is...',                  │
│              'timestamp': '10:30 AM',                │
│              'sources': '3 document chunks'          │
│          }                                           │
│      ],                                              │
│      'documents': [Chunk1, Chunk2, ...],            │
│      'vector_store': VectorStoreRAG_object,         │
│      'indices_built': True,                         │
│      'selected_rag_type': 'Vector DB RAG'           │
│  }                                                   │
└──────────────────────────────────────────────────────┘

LIFECYCLE:
User opens app → Session State created
User refreshes → Session State persists
User closes tab → Session State deleted
User reopens → New Session State created
```

---

## ⚙️ Configuration Loading Flow

```
APPLICATION STARTS
       │
       ▼
┌─────────────────┐
│ load_dotenv()   │ ← Reads .env file
└─────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ .env file:                          │
│ OPENAI_API_KEY=sk-abc123           │
│ SERPAPI_KEY=xyz789                 │
│ NEO4J_PASSWORD=neo4jpass           │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ load_config()                       │
│ Returns:                            │
│ {                                   │
│   'openai_api_key': 'sk-abc123',   │
│   'serp_api_key': 'xyz789',        │
│   'neo4j_password': 'neo4jpass'    │
│ }                                   │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ validate_config()                   │
│ Checks: All keys present?           │
│ Returns: (True, []) if valid        │
│          (False, ['MISSING_KEY'])   │
└─────────────────────────────────────┘
       │
       ▼
   Valid?
   ┌───┴───┐
   │       │
  YES      NO
   │       │
   ▼       ▼
Start    Show
App      Error
```

---

## 🔄 Complete User Journey Timeline

```
TIME: 0 seconds
┌──────────────────────────────────┐
│ User opens localhost:8501        │
└──────────────────────────────────┘

TIME: 1 second
┌──────────────────────────────────┐
│ App loads, checks .env file      │
│ ✓ All API keys present           │
└──────────────────────────────────┘

TIME: 2 seconds
┌──────────────────────────────────┐
│ Setup Wizard displayed           │
│ Step 1: Select RAG type          │
└──────────────────────────────────┘

TIME: 5 seconds
┌──────────────────────────────────┐
│ User selects "Vector DB RAG"     │
│ Step 2: Upload PDF               │
└──────────────────────────────────┘

TIME: 10 seconds
┌──────────────────────────────────┐
│ User uploads "research.pdf"      │
│ Clicks "Process PDF"             │
└──────────────────────────────────┘

TIME: 12 seconds
┌──────────────────────────────────┐
│ Processing:                      │
│ - Extract text from PDF          │
│ - Split into 47 chunks           │
│ ✓ Processed 47 chunks            │
└──────────────────────────────────┘

TIME: 15 seconds
┌──────────────────────────────────┐
│ User clicks "Build Knowledge     │
│ Base"                            │
└──────────────────────────────────┘

TIME: 20 seconds
┌──────────────────────────────────┐
│ Building:                        │
│ - Creating embeddings (OpenAI)   │
│ - Storing in FAISS vector DB     │
│ - Initializing LLM               │
│ ✓ Setup Complete! 🎉             │
└──────────────────────────────────┘

TIME: 25 seconds
┌──────────────────────────────────┐
│ Chat interface appears           │
│ User types: "What is ML?"        │
└──────────────────────────────────┘

TIME: 28 seconds
┌──────────────────────────────────┐
│ Processing:                      │
│ - Convert question to vector     │
│ - Search FAISS (0.1s)           │
│ - Retrieve 3 chunks              │
│ - Send to GPT-4 (2s)            │
│ ✓ Answer received                │
└──────────────────────────────────┘

TIME: 30 seconds
┌──────────────────────────────────┐
│ Display answer:                  │
│ "Machine learning is..."         │
│ 📚 Sources: 3 document chunks    │
└──────────────────────────────────┘
```

---

## 🎓 Learning Path Progression

```
BEGINNER (You are here!)
┌──────────────────────────────────┐
│ ✓ Understand what RAG is         │
│ ✓ Know the components            │
│ ✓ Run the application            │
│ ✓ Upload documents & ask         │
│   questions                      │
└──────────────────────────────────┘
        │
        ▼
INTERMEDIATE
┌──────────────────────────────────┐
│ □ Modify chunk size/overlap      │
│ □ Experiment with different      │
│   prompts                        │
│ □ Try all 3 RAG types            │
│ □ Compare results                │
│ □ Add new document types         │
└──────────────────────────────────┘
        │
        ▼
ADVANCED
┌──────────────────────────────────┐
│ □ Customize embedding models     │
│ □ Implement reranking            │
│ □ Add memory/history             │
│ □ Create custom tools            │
│ □ Deploy to production           │
└──────────────────────────────────┘
```

---

This visual guide shows you exactly how data flows through the RAG system!
