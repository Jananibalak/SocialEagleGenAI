# Hybrid RAG System: FAISS + Neo4j Knowledge Graph

This is a hybrid Retrieval-Augmented Generation (RAG) system that combines:
- **FAISS Vector Search** for semantic similarity
- **Neo4j Knowledge Graph** for structured relationships
- **OpenRouter API** for LLM and embeddings
- **text-embedding-3-small** for vector embeddings

## 🌟 Features

- **Dual Retrieval**: Combines semantic search (FAISS) with graph-based search (Neo4j)
- **OpenRouter Integration**: Uses OpenRouter's API for both chat and embeddings
- **Persistent Storage**: Saves FAISS index to disk for quick loading
- **Smart Context Fusion**: Merges vector and graph results for comprehensive answers

## 📋 Prerequisites

1. **Python 3.8+**
2. **Neo4j Database** (local or cloud instance)
3. **OpenRouter API Key** ([Get one here](https://openrouter.ai/))

## 🚀 Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
OPENROUTER_API_KEY=sk-or-v1-xxxxx
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

### 3. Prepare Your Data

Create a `faq.txt` file with your content. Separate Q&A pairs with blank lines:

```
What is machine learning?
Machine learning is a subset of AI that enables systems to learn from data.

What is deep learning?
Deep learning is a type of machine learning using neural networks with multiple layers.
```

## 🎯 Usage

### Run the System

```bash
python hybrid_rag.py
```

### First Run (Building Indexes)

On first run, the system will:
1. Load your `faq.txt` file
2. Create FAISS vector embeddings (saved to `faiss_index.bin`)
3. Extract entities and relationships using LLM
4. Build Neo4j knowledge graph
5. Save everything for future use

### Subsequent Runs

The system loads pre-built indexes instantly for faster startup.

### Query Examples

```
❓ Question: What is machine learning?

💡 Answer:
Machine learning is a subset of AI that enables systems to learn 
from data without explicit programming...
```

## 🔧 Configuration

### Change Models

Edit in `hybrid_rag.py`:

```python
EMBEDDING_MODEL = "text-embedding-3-small"  # OpenAI embedding model
CHAT_MODEL = "openai/gpt-4o-mini"           # Chat model via OpenRouter
EMBEDDING_DIM = 1536                        # text-embedding-3-small dimension
```

### Adjust Search Parameters

```python
# In hybrid_search function
vector_results = vector_store.search(question, top_k=3)  # Number of chunks
```

## 🏗️ Architecture

```
User Question
     |
     v
┌────────────────────────────────┐
│   Hybrid Search Engine         │
│  ┌──────────┐  ┌────────────┐ │
│  │  FAISS   │  │   Neo4j    │ │
│  │  Vector  │  │  Knowledge │ │
│  │  Search  │  │   Graph    │ │
│  └──────────┘  └────────────┘ │
└────────────────────────────────┘
     |              |
     v              v
  Semantic      Structured
  Context       Relationships
     |              |
     v──────────────v
    Combined Context
          |
          v
    LLM Generation
          |
          v
       Answer
```

## 📊 How It Works

### 1. Vector Search (FAISS)
- Converts text chunks into embeddings using `text-embedding-3-small`
- Finds semantically similar content using cosine similarity
- Returns top-k most relevant chunks

### 2. Knowledge Graph (Neo4j)
- Extracts entities (people, concepts, organizations)
- Identifies relationships between entities
- Searches for connected information based on keywords

### 3. Hybrid Retrieval
- Runs both searches in parallel
- Combines results into unified context
- LLM generates answer using both sources

## 🔄 Rebuilding Indexes

To rebuild from scratch, delete:

```bash
rm faiss_index.bin chunks.json
```

Then run the script again.

## 💾 File Structure

```
.
├── hybrid_rag.py          # Main script
├── requirements.txt       # Python dependencies
├── .env                   # Configuration (create from .env.example)
├── .env.example          # Environment template
├── faq.txt               # Your knowledge base
├── faiss_index.bin       # FAISS index (auto-generated)
└── chunks.json           # Text chunks (auto-generated)
```

## 🐛 Troubleshooting

### "Connection refused" to Neo4j
- Ensure Neo4j is running: `neo4j start`
- Check URI and credentials in `.env`

### "Invalid API key" error
- Verify your OpenRouter API key
- Check the key has sufficient credits

### Import errors
- Run: `pip install -r requirements.txt --upgrade`

## 📝 Notes

- **OpenRouter Models**: Uses OpenRouter's OpenAI-compatible endpoint
- **Embedding Model**: `text-embedding-3-small` (1536 dimensions)
- **Chat Model**: Configurable, defaults to `openai/gpt-4o-mini`
- **Persistence**: FAISS index is saved locally for faster subsequent runs

## 🎓 Use Cases

- FAQ systems with complex relationships
- Documentation search with entity connections
- Customer support with contextual understanding
- Research assistants combining semantic and structured knowledge

## 📄 License

MIT License - feel free to use and modify!
