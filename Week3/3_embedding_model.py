"""
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model="openai/text-embedding-3-small" ,api_key="*************" # cheap + good
)

vector = embeddings.embed_query("LangChain is powerful")
print(vector)
"""
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

vector = embeddings.embed_query("LangChain makes AI apps easy")
print(len(vector))
