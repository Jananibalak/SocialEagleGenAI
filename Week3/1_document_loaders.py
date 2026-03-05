from langchain_community.document_loaders import TextLoader
text = TextLoader("textfile.txt")
print(text.load())

from langchain_community.document_loaders import PyPDFLoader
text = PyPDFLoader("AI Prompt  Templates &  Practice.pdf")
print(text.load())

from langchain_community.document_loaders import WebBaseLoader  ## WEBSITE
from langchain_community.document_loaders import ArxivLoader ## RESEARCH PAPERS
from langchain_community.document_loaders import WikipediaLoader ## WIKIPEDIA