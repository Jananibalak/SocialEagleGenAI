# RAG Chatbot - Practical Exercises & Examples

## 🎯 Goal
This file contains hands-on exercises to help you understand each component of the RAG system by building it piece by piece.

---

## 📝 Exercise 1: Understanding Embeddings

### Concept
Embeddings convert text into vectors (lists of numbers) so computers can understand semantic similarity.

### Simple Example Code

```python
from langchain_openai import OpenAIEmbeddings

# Initialize embeddings model
embeddings = OpenAIEmbeddings(openai_api_key="your-key-here")

# Convert text to vectors
text1 = "I love dogs"
text2 = "I adore puppies"
text3 = "I enjoy pizza"

vector1 = embeddings.embed_query(text1)
vector2 = embeddings.embed_query(text2)
vector3 = embeddings.embed_query(text3)

print(f"Vector 1 (first 5 numbers): {vector1[:5]}")
print(f"Vector 2 (first 5 numbers): {vector2[:5]}")
print(f"Vector 3 (first 5 numbers): {vector3[:5]}")

# Calculate similarity
from numpy import dot
from numpy.linalg import norm

def cosine_similarity(vec1, vec2):
    return dot(vec1, vec2) / (norm(vec1) * norm(vec2))

sim_1_2 = cosine_similarity(vector1, vector2)  # Should be HIGH (~0.9)
sim_1_3 = cosine_similarity(vector1, vector3)  # Should be LOW (~0.3)

print(f"Similarity (dogs vs puppies): {sim_1_2}")  # Related topics
print(f"Similarity (dogs vs pizza): {sim_1_3}")    # Unrelated topics
```

**Expected Output:**
```
Vector 1 (first 5 numbers): [0.023, -0.015, 0.891, -0.234, 0.567]
Vector 2 (first 5 numbers): [0.019, -0.012, 0.887, -0.229, 0.563]
Vector 3 (first 5 numbers): [0.341, 0.678, -0.123, 0.456, -0.234]

Similarity (dogs vs puppies): 0.94  ← Very similar!
Similarity (dogs vs pizza): 0.23     ← Not similar
```

### ✏️ Your Turn
1. Try three sentences of your own
2. Predict which two will have the highest similarity
3. Run the code and check if you were right!

---

## 📝 Exercise 2: Document Chunking

### Concept
Break large documents into smaller pieces for better retrieval.

### Simple Example Code

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Sample document
document = """
Machine learning is a subset of artificial intelligence. 
It focuses on building systems that learn from data. 
These systems improve their performance over time without being explicitly programmed.

There are three main types of machine learning:
1. Supervised learning uses labeled data
2. Unsupervised learning finds patterns in unlabeled data
3. Reinforcement learning learns through trial and error

Applications include image recognition, natural language processing, and recommendation systems.
"""

# Create text splitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,      # Maximum characters per chunk
    chunk_overlap=20,    # Characters to overlap between chunks
    separators=["\n\n", "\n", ". ", " "]  # Split priority
)

# Split the document
chunks = splitter.split_text(document)

# Display results
print(f"Original document length: {len(document)} characters")
print(f"Number of chunks: {len(chunks)}\n")

for i, chunk in enumerate(chunks, 1):
    print(f"--- Chunk {i} ({len(chunk)} chars) ---")
    print(chunk)
    print()
```

**Expected Output:**
```
Original document length: 487 characters
Number of chunks: 6

--- Chunk 1 (98 chars) ---
Machine learning is a subset of artificial intelligence. 
It focuses on building systems that

--- Chunk 2 (95 chars) ---
that learn from data. 
These systems improve their performance over time without being explicitly

--- Chunk 3 (99 chars) ---
without being explicitly programmed.

There are three main types of machine learning:
1. Supervised

--- Chunk 4 (91 chars) ---
1. Supervised learning uses labeled data
2. Unsupervised learning finds patterns in unlabeled

--- Chunk 5 (93 chars) ---
in unlabeled data
3. Reinforcement learning learns through trial and error

Applications include

--- Chunk 6 (75 chars) ---
Applications include image recognition, natural language processing, and recommendation
```

### ✏️ Your Turn
1. Change `chunk_size` to 50 and 200. How does it affect the chunks?
2. Change `chunk_overlap` to 0 and 50. What's the difference?
3. Why is overlap important? (Hint: Look at chunk boundaries)

---

## 📝 Exercise 3: Simple Vector Search

### Concept
Store documents as vectors and search for similar ones.

### Simple Example Code

```python
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# Sample documents about different topics
documents = [
    Document(page_content="Python is a programming language used for web development and data science."),
    Document(page_content="Machine learning algorithms can predict future outcomes based on historical data."),
    Document(page_content="The Eiffel Tower is located in Paris, France."),
    Document(page_content="Neural networks are inspired by the human brain and consist of interconnected nodes."),
    Document(page_content="Pandas is a Python library for data manipulation and analysis."),
]

# Create embeddings
embeddings = OpenAIEmbeddings(openai_api_key="your-key-here")

# Create vector store
vectorstore = FAISS.from_documents(documents, embeddings)

# Search for similar documents
query = "What is a good Python library for data?"

results = vectorstore.similarity_search(query, k=2)  # Get top 2 results

print(f"Query: {query}\n")
print("Top Results:")
for i, doc in enumerate(results, 1):
    print(f"{i}. {doc.page_content}")
```

**Expected Output:**
```
Query: What is a good Python library for data?

Top Results:
1. Pandas is a Python library for data manipulation and analysis.
2. Python is a programming language used for web development and data science.
```

### ✏️ Your Turn
1. Try query: "Tell me about artificial intelligence"
2. Which documents do you expect to rank highest?
3. Change `k=2` to `k=3`. Does the third result make sense?

---

## 📝 Exercise 4: Simple RAG Pipeline

### Concept
Combine document retrieval with LLM generation.

### Simple Example Code

```python
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# Step 1: Create knowledge base
documents = [
    Document(page_content="The capital of France is Paris."),
    Document(page_content="The Eiffel Tower is 324 meters tall."),
    Document(page_content="Paris is known as the City of Light."),
    Document(page_content="The Louvre Museum is in Paris."),
]

embeddings = OpenAIEmbeddings(openai_api_key="your-key-here")
vectorstore = FAISS.from_documents(documents, embeddings)

# Step 2: Initialize LLM
llm = ChatOpenAI(temperature=0, openai_api_key="your-key-here")

# Step 3: Define RAG function
def simple_rag(question: str) -> str:
    # Retrieve relevant documents
    relevant_docs = vectorstore.similarity_search(question, k=2)
    
    # Combine documents into context
    context = "\n".join([doc.page_content for doc in relevant_docs])
    
    # Create prompt
    prompt = f"""Answer the question based only on the following context:

Context:
{context}

Question: {question}

Answer:"""
    
    # Get response
    response = llm.invoke(prompt)
    
    return response.content

# Step 4: Test it!
question1 = "What is the capital of France?"
question2 = "How tall is the Eiffel Tower?"
question3 = "What is Paris known as?"

print(f"Q: {question1}")
print(f"A: {simple_rag(question1)}\n")

print(f"Q: {question2}")
print(f"A: {simple_rag(question2)}\n")

print(f"Q: {question3}")
print(f"A: {simple_rag(question3)}\n")
```

**Expected Output:**
```
Q: What is the capital of France?
A: The capital of France is Paris.

Q: How tall is the Eiffel Tower?
A: The Eiffel Tower is 324 meters tall.

Q: What is Paris known as?
A: Paris is known as the City of Light.
```

### ✏️ Your Turn
1. Add a new document: "The Seine River flows through Paris."
2. Ask: "Is there a river in Paris?"
3. Does it answer correctly?

---

## 📝 Exercise 5: Loading a Real PDF

### Concept
Load and process an actual PDF file.

### Simple Example Code

```python
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load PDF (replace with your PDF path)
loader = PyPDFLoader("your_document.pdf")
documents = loader.load()

print(f"Number of pages: {len(documents)}")
print(f"\nFirst page preview:")
print(documents[0].page_content[:300])  # First 300 characters
print("...")

# Split into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = text_splitter.split_documents(documents)

print(f"\nTotal chunks created: {len(chunks)}")
print(f"\nFirst chunk:")
print(chunks[0].page_content)
```

### ✏️ Your Turn
1. Download any PDF (a research paper, manual, or ebook)
2. Load it using the code above
3. How many chunks are created?
4. Read the first few chunks - do they make sense?

---

## 📝 Exercise 6: Comparing RAG vs No-RAG

### Concept
See the difference between using RAG and not using RAG.

### Simple Example Code

```python
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# Your specific knowledge (not in GPT's training data)
documents = [
    Document(page_content="Our company's Q4 revenue was $5.2 million."),
    Document(page_content="We launched Product X on January 15, 2024."),
    Document(page_content="Our CEO is Jane Smith."),
]

embeddings = OpenAIEmbeddings(openai_api_key="your-key-here")
vectorstore = FAISS.from_documents(documents, embeddings)
llm = ChatOpenAI(temperature=0, openai_api_key="your-key-here")

question = "What was our Q4 revenue?"

# WITHOUT RAG - Just ask the LLM
print("=== WITHOUT RAG ===")
response_no_rag = llm.invoke(question)
print(response_no_rag.content)
print()

# WITH RAG - Retrieve context first
print("=== WITH RAG ===")
relevant_docs = vectorstore.similarity_search(question, k=1)
context = relevant_docs[0].page_content

prompt = f"""Based on this context: {context}

Question: {question}

Answer:"""

response_with_rag = llm.invoke(prompt)
print(response_with_rag.content)
```

**Expected Output:**
```
=== WITHOUT RAG ===
I don't have access to specific company financial data. Could you please provide 
more context about which company you're referring to?

=== WITH RAG ===
Based on the provided context, the Q4 revenue was $5.2 million.
```

### ✏️ Your Turn
1. Create 3 facts about your imaginary company
2. Ask questions that require this specific information
3. Compare answers with and without RAG

---

## 📝 Exercise 7: Understanding Session State

### Concept
Session state preserves data between interactions.

### Simple Example Code (Streamlit)

```python
import streamlit as st

# Initialize session state
if 'counter' not in st.session_state:
    st.session_state.counter = 0

if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display current state
st.write(f"Counter: {st.session_state.counter}")

# Button to increment
if st.button("Increment"):
    st.session_state.counter += 1
    st.rerun()

# Button to reset
if st.button("Reset"):
    st.session_state.counter = 0
    st.rerun()

# Add message
message = st.text_input("Enter a message:")
if st.button("Add Message"):
    st.session_state.messages.append(message)
    st.rerun()

# Display messages
st.write("Message History:")
for msg in st.session_state.messages:
    st.write(f"- {msg}")
```

### ✏️ Your Turn
1. Run this code
2. Click "Increment" multiple times
3. Refresh the page - what happens to the counter?
4. Add several messages
5. What would happen if we didn't use session_state?

---

## 📝 Exercise 8: Simple Knowledge Graph

### Concept
Store information as entities and relationships.

### Simple Example Code

```python
# Represent a simple knowledge graph as a dictionary
knowledge_graph = {
    "Elon Musk": {
        "type": "Person",
        "founded": ["Tesla", "SpaceX"],
        "role": "CEO"
    },
    "Tesla": {
        "type": "Company",
        "founded_by": "Elon Musk",
        "products": ["Model S", "Model 3", "Model X"]
    },
    "SpaceX": {
        "type": "Company",
        "founded_by": "Elon Musk",
        "products": ["Falcon 9", "Starship"]
    }
}

# Query function
def query_graph(question: str) -> str:
    if "founded" in question.lower() and "elon musk" in question.lower():
        companies = knowledge_graph["Elon Musk"]["founded"]
        return f"Elon Musk founded: {', '.join(companies)}"
    
    elif "products" in question.lower() and "tesla" in question.lower():
        products = knowledge_graph["Tesla"]["products"]
        return f"Tesla products: {', '.join(products)}"
    
    elif "ceo" in question.lower():
        for person, data in knowledge_graph.items():
            if data.get("role") == "CEO":
                return f"The CEO is {person}"
    
    return "I don't know the answer to that."

# Test queries
print(query_graph("What companies did Elon Musk found?"))
print(query_graph("What are Tesla's products?"))
print(query_graph("Who is the CEO?"))
```

**Expected Output:**
```
Elon Musk founded: Tesla, SpaceX
Tesla products: Model S, Model 3, Model X
The CEO is Elon Musk
```

### ✏️ Your Turn
1. Add a new person: "Tim Cook" (Apple CEO)
2. Add Apple's products: iPhone, iPad, Mac
3. Write a query to ask "What are Apple's products?"

---

## 📝 Exercise 9: Debugging RAG

### Concept
Learn to debug and understand what's happening in RAG.

### Simple Example Code

```python
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# Sample documents
documents = [
    Document(page_content="The sky is blue because of Rayleigh scattering."),
    Document(page_content="Photosynthesis converts sunlight into chemical energy."),
    Document(page_content="Water boils at 100 degrees Celsius at sea level."),
]

embeddings = OpenAIEmbeddings(openai_api_key="your-key-here")
vectorstore = FAISS.from_documents(documents, embeddings)
llm = ChatOpenAI(temperature=0, openai_api_key="your-key-here")

def debug_rag(question: str):
    print("=" * 60)
    print(f"QUESTION: {question}")
    print("=" * 60)
    
    # Step 1: Retrieve
    print("\n[STEP 1: RETRIEVAL]")
    relevant_docs = vectorstore.similarity_search(question, k=2)
    print(f"Found {len(relevant_docs)} relevant documents:")
    for i, doc in enumerate(relevant_docs, 1):
        print(f"{i}. {doc.page_content}")
    
    # Step 2: Create context
    print("\n[STEP 2: CONTEXT]")
    context = "\n".join([doc.page_content for doc in relevant_docs])
    print(context)
    
    # Step 3: Create prompt
    print("\n[STEP 3: PROMPT]")
    prompt = f"""Answer based on this context:

{context}

Question: {question}

Answer:"""
    print(prompt)
    
    # Step 4: Get answer
    print("\n[STEP 4: ANSWER]")
    answer = llm.invoke(prompt).content
    print(answer)
    
    return answer

# Test with different questions
debug_rag("Why is the sky blue?")
debug_rag("What happens during photosynthesis?")
debug_rag("At what temperature does water boil?")
```

**This will show you:**
- Which documents were retrieved
- What context was sent to the LLM
- The exact prompt used
- The final answer

### ✏️ Your Turn
1. Run this with your own documents
2. Try a question that SHOULD find the right document
3. Try a question that WON'T find the right document
4. Observe what gets retrieved in each case

---

## 📝 Exercise 10: Build Your Own Mini-RAG

### Challenge
Combine everything you've learned to build a simple RAG system from scratch.

### Requirements
1. Load 5 documents (can be hardcoded strings)
2. Split them into chunks
3. Create a vector store
4. Write a query function
5. Test with 3 questions

### Template Code

```python
# Import necessary libraries
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Your code here:
# 1. Create documents
documents = [
    # Add your 5 documents
]

# 2. (Optional) Split into chunks
# text_splitter = ...

# 3. Create embeddings and vector store
# embeddings = ...
# vectorstore = ...

# 4. Create LLM
# llm = ...

# 5. Define query function
def my_rag_query(question: str) -> str:
    # Your implementation
    pass

# 6. Test with questions
questions = [
    # Add your 3 test questions
]

for q in questions:
    print(f"Q: {q}")
    print(f"A: {my_rag_query(q)}")
    print()
```

### ✏️ Your Turn
Fill in the template and make it work!

**Hints:**
- Keep it simple first
- Test each step individually
- Use `print()` statements to debug
- Don't worry about making it perfect

---

## 🎓 Additional Challenges

### Challenge 1: Multi-Document RAG
Load 2-3 different PDF files and build a RAG system that can answer questions from any of them.

### Challenge 2: Source Attribution
Modify the RAG system to not just give an answer, but also tell you which specific document the answer came from.

### Challenge 3: Confidence Scoring
Add a feature that rates how confident the system is in its answer (based on similarity scores).

### Challenge 4: Hybrid Search
Combine vector search with keyword search for better results.

### Challenge 5: Conversation Memory
Make the RAG system remember previous questions in the conversation.

---

## 📚 Resources for Practice

### Free Datasets to Try:
1. **Wikipedia articles** - Download any topic
2. **Research papers** - From arxiv.org
3. **Books** - From Project Gutenberg
4. **News articles** - Any news website
5. **Your own notes** - Personal knowledge base

### Suggested Projects:
1. **Personal Assistant**: RAG on your notes/documents
2. **Study Buddy**: RAG on textbooks
3. **Company KB**: RAG on company docs/policies
4. **Recipe Finder**: RAG on recipe books
5. **Code Helper**: RAG on programming documentation

---

## ✅ Knowledge Checks

After completing these exercises, you should be able to:

- [ ] Explain what embeddings are
- [ ] Split documents into chunks
- [ ] Create a vector store
- [ ] Perform similarity search
- [ ] Build a basic RAG pipeline
- [ ] Load and process PDFs
- [ ] Understand the difference between RAG and no-RAG
- [ ] Use session state in Streamlit
- [ ] Debug RAG systems
- [ ] Build a mini-RAG from scratch

If you can check all these boxes, you're ready to work with more advanced RAG systems!

---

## 🚀 Next Steps

1. **Experiment**: Modify the chat.py code
2. **Build**: Create your own RAG project
3. **Learn More**: 
   - Vector databases (Pinecone, Weaviate)
   - Advanced chunking strategies
   - Hybrid search
   - Multi-query retrieval
   - Reranking techniques

Happy learning! 🎉
