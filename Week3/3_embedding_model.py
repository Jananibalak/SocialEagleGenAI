"""
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model="openai/text-embedding-3-small" ,api_key="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" # cheap + good
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
