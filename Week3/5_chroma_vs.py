from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# Step 1: Embedding model (runs locally)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Step 2: Sample documents
docs = [
    Document(page_content="LangChain helps build LLM powered applications."),
    Document(page_content="Chroma is a vector database for AI applications."),
    Document(page_content="Embeddings convert text into numerical vectors."),
    Document(page_content="Groq provides ultra fast AI inference.")
]
"""
# Step 3: Create Chroma DB (with persistence)
vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    persist_directory="chroma_db"   # folder where DB is stored
)

# Step 4: Similarity search
results = vectorstore.similarity_search("What is Chroma?", k=2)

for i, doc in enumerate(results, 1):
    print(f"\nResult {i}: {doc.page_content}")

"""
    ##later


vectorstore = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings
)

results = vectorstore.similarity_search("Explain embeddings")
print(results[0].page_content)

retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
docs = retriever.invoke("What does Chroma do?")
print(docs[0].page_content)


