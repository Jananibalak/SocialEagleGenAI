# Quick Start Guide 🚀

Get your RAG system running in 5 minutes!

## Step 1: Install Dependencies

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

## Step 2: Start Neo4j

### Using Docker (Easiest):
```bash
docker-compose up -d
```

### Or Install Locally:
Download from https://neo4j.com/download/ and start the database

## Step 3: Get API Keys

1. **OpenAI**: https://platform.openai.com/api-keys
2. **SerpAPI**: https://serpapi.com/manage-api-key (100 free searches/month)

## Step 4: Run the App

```bash
streamlit run app.py
```

## Step 5: Configure in Browser

1. Open http://localhost:8501
2. Enter API keys in sidebar:
   - OpenAI API Key
   - SerpAPI Key
   - Neo4j Password (default: password123)
3. Upload a PDF or enter a URL
4. Click "Build RAG Indices"
5. Ask questions!

## Test with Sample Questions

After uploading a document, try:

- "What is this document about?"
- "Summarize the main points"
- "What are the key entities mentioned?"
- Use "Compare All" to see all three RAG systems in action

## Troubleshooting

### Can't connect to Neo4j?
```bash
# Check if Neo4j is running
docker ps  # Should see neo4j-rag container

# View Neo4j browser
# Open http://localhost:7474
# Login: neo4j / password123
```

### OpenAI API errors?
- Check your API key is valid
- Ensure you have credits in your OpenAI account
- Try switching to openai/gpt-4o-mini if hitting rate limits

### File too large?
- PDF limit is 500KB
- Use a smaller document or extract specific pages
- Alternatively, load content from a URL

## Example Workflow

1. Upload: research_paper.pdf
2. Build indices (takes 30-60 seconds)
3. Ask: "What are the main findings?"
4. Compare: Switch to "Compare All" to see different approaches
5. Try Agentic: Ask "What are recent developments in this field?" 
   (will use web search for current info)

## Need Help?

- Check README.md for detailed documentation
- Review error messages in the Streamlit interface
- Ensure all API keys are correctly entered
