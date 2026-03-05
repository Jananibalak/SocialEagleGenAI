from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

splittext = PyPDFLoader("LangChain.pdf")
full_doc = splittext.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=0)
docs = text_splitter.split_documents(full_doc)

print("Chunks created:", len(docs))



embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    persist_directory="chroma_db"
)

print("Vector DB created and saved!")

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

query = "What is the main topic of the document?"

results = retriever.invoke(query) #invoke

for i, doc in enumerate(results, 1):
    print(f"\nResult {i}:\n{doc.page_content[:300]}...")
