# Knowledge Graph RAG System

A production-ready Retrieval-Augmented Generation (RAG) system powered by Knowledge Graphs, LLMs, and Neo4j.

## 🎯 What This Does

Automatically extracts entities and relationships from documents, builds a knowledge graph, and answers questions using graph-based context retrieval.

**Example:**
```
Document: "Amazon was founded by Jeff Bezos in 1994 in Seattle..."

Graph Created:
(Jeff Bezos:Person) -[FOUNDED]-> (Amazon:Organization) -[LOCATED_IN]-> (Seattle:Location)

Query: "Who founded Amazon?"
Answer: "Jeff Bezos founded Amazon in 1994 in Seattle, Washington."
```

## ✨ Features

- **🤖 AI-Powered Extraction**: Uses GPT-4o-mini to extract entities and relationships
- **📊 Knowledge Graph Storage**: Stores structured knowledge in Neo4j graph database
- **🔍 Fuzzy Search**: Finds entities with partial names ("jassy" → "Andy Jassy")
- **⏰ Temporal Reasoning**: Tracks when relationships were valid (CEO from 1994-2021)
- **🔗 Multi-hop Queries**: Finds connections across multiple relationships
- **💬 Natural Language Queries**: Ask questions in plain English

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Docker Desktop (for Neo4j)
- OpenRouter API key

### Installation

1. **Clone/Setup Project**
```bash
mkdir knowledge-graph-rag
cd knowledge-graph-rag
```

2. **Install Dependencies**
```bash
pip install langchain langchain-community neo4j openai python-dotenv
```

3. **Start Neo4j**
```bash
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  neo4j:latest
```

4. **Configure Environment**

Create `.env` file:
```env
OPENROUTER_API_KEY=your_key_here
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

5. **Create Sample Document**

Create `knowledge_base.txt`:
```
Amazon was founded by Jeff Bezos in 1994 in Seattle, Washington.
Jeff Bezos served as CEO until 2021, when Andy Jassy took over as CEO.
```

### Usage

**Build Knowledge Graph:**
```bash
python pipeline.py
```

**Query the Graph:**
```bash
python advanced_rag.py
```

**Example Queries:**
- "Who founded Amazon?"
- "When did Andy Jassy become CEO?"
- "Tell me about Jeff Bezos"
- "What companies are in Seattle?"

## 📁 Project Structure
```
knowledge-graph-rag/
├── .env                    # API keys and configuration
├── config.py               # Configuration loader
├── extract_knowledge.py    # LLM-powered entity extraction
├── graph_builder.py        # Neo4j graph operations
├── pipeline.py             # End-to-end document processing
├── advanced_rag.py         # RAG query system with fuzzy matching
├── knowledge_base.txt      # Sample document
└── docs/                   # Documentation
    ├── ARCHITECTURE.md
    ├── API_REFERENCE.md
    └── TUTORIAL.md
```

## 🏗️ Architecture
```
Document → Extract Entities/Relationships → Store in Neo4j → Query → Answer
            (GPT-4o-mini)                    (Graph DB)      (RAG)
```

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.

## 📖 Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design and data flow
- **[API_REFERENCE.md](docs/API_REFERENCE.md)** - Code documentation
- **[TUTORIAL.md](docs/TUTORIAL.md)** - Step-by-step learning guide
- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Production deployment

## 🔧 Key Components

### 1. Knowledge Extraction (`extract_knowledge.py`)
Extracts structured knowledge from text using LLM:
```python
from extract_knowledge import KnowledgeExtractor

extractor = KnowledgeExtractor()
knowledge = extractor.extract_from_text("Amazon was founded by Jeff Bezos in 1994")
# Returns: {"entities": [...], "relationships": [...]}
```

### 2. Graph Building (`graph_builder.py`)
Stores knowledge in Neo4j:
```python
from graph_builder import GraphBuilder

builder = GraphBuilder(uri, user, password)
builder.build_from_knowledge(knowledge)
```

### 3. Pipeline (`pipeline.py`)
End-to-end processing:
```python
from pipeline import KnowledgeGraphPipeline

pipeline = KnowledgeGraphPipeline()
pipeline.process_document("document.txt")
```

### 4. RAG Query (`advanced_rag.py`)
Answer questions using graph context:
```python
from advanced_rag import AdvancedRAGSystem

rag = AdvancedRAGSystem()
response = rag.query("Who founded Amazon?")
print(response["answer"])
```

## 🎓 Example Workflow

### 1. Build Graph from Document
```bash
python pipeline.py
```

Output:
```
Processing 3 chunks...
✓ Extracted: 5 entities, 4 relationships
✓ Created: Jeff Bezos (Person)
✓ Created: Amazon (Organization)
✓ Jeff Bezos --[FOUNDED]--> Amazon [1994 → present]
```

### 2. Query the Graph
```bash
python advanced_rag.py
```
```
💬 Your question: who is jassy?

[Step 1] Extracting entities with fuzzy matching...
   'jassy' → Andy Jassy

[Step 2] Retrieving context...
   Entity: Andy Jassy (Person)
   - CEO of Amazon (2021 → present)

[Step 3] Generating answer...
🤖 ANSWER: Andy Jassy became CEO of Amazon in 2021, taking over from Jeff Bezos.
```

## 🔍 Neo4j Browser

Visualize your graph:

1. Open: http://localhost:7474/browser/
2. Run query:
```cypher
MATCH (n) RETURN n LIMIT 50
```

## 🧪 Testing

Test individual components:
```bash
# Test extraction
python extract_knowledge.py

# Test graph builder
python graph_builder.py

# Test configuration
python config.py
```

## 🛠️ Configuration

Edit `.env` to configure:
```env
# LLM Configuration
OPENROUTER_API_KEY=your_key
MODEL_NAME=openai/gpt-4o-mini

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

## 📊 Supported Features

### Entity Types
- ✅ Person
- ✅ Organization
- ✅ Location
- ✅ Product

### Relationship Types
- ✅ FOUNDED
- ✅ CEO_OF
- ✅ WORKS_AT
- ✅ LOCATED_IN
- ✅ LED
- ✅ Custom types (auto-detected)

### Query Capabilities
- ✅ Fuzzy entity matching
- ✅ Multi-hop traversal (1-3 hops)
- ✅ Temporal queries (when was X true?)
- ✅ Path finding (how are X and Y connected?)
- ✅ Property filtering

## 🚀 Advanced Usage

### Process Multiple Documents
```python
pipeline.process_multiple_documents(
    directory="./documents",
    file_pattern="*.txt",
    chunking_method="paragraph"
)
```

### Custom Chunking
```python
pipeline.process_document(
    filepath="document.txt",
    chunking_method="sentence"  # or "fixed_size"
)
```

### Search Entities
```python
matches = rag.fuzzy_search_entities("bezos", limit=5)
for match in matches:
    print(f"{match['name']} - Score: {match['relevance']}")
```

## 🐛 Troubleshooting

### Neo4j Connection Failed
```
Error: Failed to connect to Neo4j
```
**Solution:** Check Docker container is running:
```bash
docker ps
docker start neo4j
```

### API Key Error
```
Error: OPENROUTER_API_KEY not found
```
**Solution:** Check `.env` file exists and contains valid API key

### Entity Not Found
```
Entity 'amazon' not found in knowledge graph
```
**Solution:** Graph uses exact names. Try:
- Proper capitalization: "Amazon" not "amazon"
- Full name: "Andy Jassy" not "jassy"
- Or use fuzzy search in `advanced_rag.py`

## 📈 Performance

- **Extraction Speed**: ~2-5 seconds per paragraph (depends on LLM)
- **Graph Storage**: ~100ms per entity/relationship
- **Query Speed**: ~500ms-2s (depends on graph size and hops)

## 🔐 Security

**Production Recommendations:**
- Never commit `.env` file (add to `.gitignore`)
- Use environment variables for secrets
- Implement API rate limiting
- Add authentication for deployed services
- Use HTTPS for API endpoints

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- [ ] PDF/DOCX document support
- [ ] Graph visualization UI
- [ ] Batch processing optimization
- [ ] Entity resolution/deduplication
- [ ] Graph analytics (PageRank, community detection)

## 📄 License

MIT License - See LICENSE file

## 🙏 Acknowledgments

- **Neo4j** - Graph database
- **OpenRouter** - LLM API gateway
- **LangChain** - LLM framework
- **OpenAI** - GPT models

## 📞 Support

- Create an issue for bugs
- Check documentation in `/docs`
- Review examples in code files

## 🎯 Next Steps
2. Review [ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design
3. Check [API_REFERENCE.md](docs/API_REFERENCE.md) for code details
4. See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for production setup

---

**Built with ❤️ using Knowledge Graphs, LLMs, and Neo4j**