# Advanced RAG System 🤖

A comprehensive Retrieval-Augmented Generation (RAG) system built with Streamlit that supports multiple retrieval strategies:

- **Vector DB RAG**: Semantic search using FAISS
- **Knowledge Graph RAG**: Entity-relationship based retrieval using Neo4j
- **Agentic RAG**: Intelligent agent with web search fallback using SerpAPI
- **Comparison Mode**: Compare all three approaches side-by-side

## Features ✨

- 📁 **Multiple Input Sources**: Upload PDFs or load content from URLs
- 🔍 **Three RAG Approaches**: Vector search, knowledge graphs, and agentic reasoning
- 🌐 **Web Search Fallback**: Automatically searches the web when local knowledge is insufficient
- 📊 **Comparison Mode**: Evaluate different RAG strategies on the same question
- 🛡️ **Error Handling**: Robust error handling throughout the pipeline
- 📏 **File Size Limit**: 500KB max for PDF uploads
- 💬 **Interactive UI**: Clean Streamlit interface for easy interaction

## Prerequisites 📋

Before running the application, you'll need:

1. **Python 3.8+**
2. **Neo4j Database** (running locally or remotely)
3. **API Keys**:
   - OpenAI API key
   - SerpAPI key

## Installation 🔧

### 1. Clone or Download the Repository

```bash
# If you have the files
cd rag-streamlit-app
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Neo4j

#### Option A: Docker (Recommended)

```bash
docker run \
    --name neo4j \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/your_password \
    -e NEO4J_PLUGINS='["apoc"]' \
    neo4j:latest
```

#### Option B: Download Neo4j Desktop

1. Download from [Neo4j Download Center](https://neo4j.com/download/)
2. Install and create a new database
3. Set password and start the database
4. Note the bolt URI (usually `bolt://localhost:7687`)

### 5. Get API Keys

#### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key

#### SerpAPI Key
1. Go to [SerpAPI](https://serpapi.com/)
2. Sign up for a free account (100 searches/month free)
3. Get your API key from the dashboard

## Configuration ⚙️

### Environment Variables (Optional)

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
SERPAPI_KEY=your_serpapi_key_here
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password
```

## Usage 🚀

### 1. Start the Application

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### 2. Configure API Keys

In the sidebar, enter your:
- OpenAI API Key
- SerpAPI Key
- Neo4j connection details (URI, username, password)

### 3. Upload Documents

Choose one of two options:
- **Upload PDF**: Select a PDF file (max 500KB)
- **Load from URL**: Enter a web URL to scrape content

Click the processing button to load and chunk your documents.

### 4. Build RAG Indices

Click the **"🔨 Build RAG Indices"** button to:
- Create FAISS vector store
- Build Neo4j knowledge graph
- Prepare data for querying

### 5. Query Your Data

1. Select a RAG type:
   - Vector DB RAG (semantic search)
   - Knowledge Graph RAG (entity relationships)
   - Agentic RAG (intelligent agent with web search)
   - Compare All (side-by-side comparison)

2. Enter your question

3. Click **"Get Answer"** to see results

## Architecture 🏗️

### Vector DB RAG (FAISS)
```
Documents → Chunking → Embeddings → FAISS Index
                                        ↓
User Query → Embedding → Similarity Search → Top-k Documents
                                                   ↓
                                              LLM → Answer
```

### Knowledge Graph RAG (Neo4j)
```
Documents → Entity Extraction → Neo4j Graph
                                    ↓
User Query → Entity Extraction → Graph Traversal → Context
                                                       ↓
                                                  LLM → Answer
```

### Agentic RAG
```
User Query → Agent (ReAct)
              ├─ Tool 1: Search Documents (FAISS)
              ├─ Tool 2: Web Search (SerpAPI)
              └─ Decision Logic
                   ↓
              Synthesized Answer
```

## Error Handling 🛡️

The application includes comprehensive error handling:

- **File Size Validation**: Rejects PDFs over 500KB
- **API Connection Errors**: Graceful handling of API failures
- **Database Connection**: Validates Neo4j connectivity
- **Web Search Fallback**: Falls back to web search if agent fails
- **Document Processing**: Handles malformed PDFs and URLs
- **Empty Results**: Informative messages when no results found

## Troubleshooting 🔧

### Neo4j Connection Issues

```python
# Test Neo4j connection
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "your_password")
)
driver.verify_connectivity()
print("Connected!")
```

### FAISS Installation Issues

If FAISS fails to install:
```bash
# On macOS with Apple Silicon
pip install faiss-cpu --no-cache-dir

# Alternative: use conda
conda install -c pytorch faiss-cpu
```

### OpenAI Rate Limits

If you hit rate limits:
- Upgrade your OpenAI plan
- Reduce chunk size to minimize API calls
- Use openai/gpt-4o-mini instead of GPT-4

## Customization 🎨

### Adjust Chunk Size

In `app.py`, modify the `chunk_documents` function:

```python
def chunk_documents(documents, chunk_size=1000, chunk_overlap=200):
    # Increase chunk_size for longer contexts
    # Increase chunk_overlap for better continuity
```

### Change LLM Model

```python
# In VectorRAG, KnowledgeGraphRAG, or AgenticRAG classes
self.llm = ChatOpenAI(
    temperature=0,
    model_name="gpt-4",  # Change to gpt-4, openai/gpt-4o-mini, etc.
    openai_api_key=api_key
)
```

### Modify Retrieval Parameters

```python
# Number of documents to retrieve
k = 3  # Change to retrieve more/fewer documents

# In similarity search
self.vector_store.as_retriever(search_kwargs={"k": k})
```

## Performance Tips ⚡

1. **Start with Vector DB RAG**: Fastest and most reliable
2. **Use Knowledge Graph for Entity-Heavy Documents**: Better for documents with many relationships
3. **Reserve Agentic RAG for Complex Queries**: More capable but slower
4. **Chunk Size Matters**: 
   - Smaller chunks (500-1000): Better precision
   - Larger chunks (1500-2000): Better context

## Limitations ⚠️

- PDF size limited to 500KB (configurable)
- Neo4j entity extraction depends on LLM quality
- SerpAPI free tier: 100 searches/month
- OpenAI API costs apply per query
- Knowledge graph quality depends on document structure

## Future Enhancements 🚧

- [ ] Support for more file types (DOCX, TXT, CSV)
- [ ] Hybrid search (combining vector + keyword)
- [ ] Chat history and follow-up questions
- [ ] Export results to PDF/markdown
- [ ] Multi-language support
- [ ] Custom entity extraction models
- [ ] Local LLM support (Ollama, LlamaCPP)

## License 📄

MIT License - Feel free to use and modify!

## Contributing 🤝

Contributions are welcome! Please feel free to submit issues or pull requests.

## Support 💬

For questions or issues:
1. Check the troubleshooting section
2. Review error messages in the Streamlit interface
3. Open an issue on GitHub

## Acknowledgments 🙏

Built with:
- [Streamlit](https://streamlit.io/)
- [LangChain](https://langchain.com/)
- [FAISS](https://github.com/facebookresearch/faiss)
- [Neo4j](https://neo4j.com/)
- [OpenAI](https://openai.com/)
- [SerpAPI](https://serpapi.com/)
