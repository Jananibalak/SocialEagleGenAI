from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# Step 1: Load embedding model (runs locally)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Step 2: Create sample documents
docs = [
    Document(page_content="LangChain helps build LLM powered applications."),
    Document(page_content="FAISS is a library for efficient similarity search."),
    Document(page_content="Embeddings convert text into numerical vectors.")
]

# Step 3: Create FAISS vector store
#vectorstore = FAISS.from_documents(docs, embeddings)
#vectorstore.save_local("myLocalVector")

# Step 4: Perform similarity search
#query = "What is FAISS used for?"
#results = vectorstore.similarity_search(query, k=2)
"""
# Step 5: Print results
for i, doc in enumerate(results, 1):
    print(f"\nResult {i}:")
    print(doc.page_content)
"""
vectorstore = FAISS.load_local(
    "myLocalVector",
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
docs = retriever.invoke("Explain embeddings")
print(docs[0].page_content)



