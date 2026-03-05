import os, json
import numpy as np
import faiss
from openai import OpenAI
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenRouter client (OpenAI-compatible)
ai = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# Initialize Neo4j
db = GraphDatabase.driver(
    os.getenv("NEO4J_URI"), 
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

# Configuration
EMBEDDING_MODEL = "text-embedding-3-small"  # OpenRouter supports OpenAI embedding models
CHAT_MODEL = "openai/gpt-4o-mini"  # OpenRouter model format
EMBEDDING_DIM = 1536  # text-embedding-3-small dimension

# ─────────────────────────────────────────────
# VECTOR STORE (FAISS)
# ─────────────────────────────────────────────
class VectorStore:
    def __init__(self):
        self.index = faiss.IndexFlatL2(EMBEDDING_DIM)
        self.chunks = []
        self.embeddings = []
    
    def get_embedding(self, text):
        """Get embedding from OpenRouter"""
        response = ai.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return np.array(response.data[0].embedding, dtype='float32')
    
    def add_chunks(self, chunks):
        """Add text chunks to FAISS index"""
        print(f"🔢 Embedding {len(chunks)} chunks...")
        for i, chunk in enumerate(chunks):
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(chunks)}")
            
            embedding = self.get_embedding(chunk)
            self.chunks.append(chunk)
            self.embeddings.append(embedding)
        
        # Add to FAISS index
        embeddings_matrix = np.vstack(self.embeddings)
        self.index.add(embeddings_matrix)
        print(f"✅ Added {len(chunks)} chunks to vector store")
    
    def search(self, query, top_k=3):
        """Search for similar chunks"""
        query_embedding = self.get_embedding(query).reshape(1, -1)
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.chunks):
                results.append({
                    'chunk': self.chunks[idx],
                    'score': float(dist)
                })
        return results
    
    def save(self, index_path="faiss_index.bin", chunks_path="chunks.json"):
        """Save FAISS index and chunks"""
        faiss.write_index(self.index, index_path)
        with open(chunks_path, 'w') as f:
            json.dump(self.chunks, f)
        print(f"💾 Saved vector store to {index_path}")
    
    def load(self, index_path="faiss_index.bin", chunks_path="chunks.json"):
        """Load FAISS index and chunks"""
        if os.path.exists(index_path) and os.path.exists(chunks_path):
            self.index = faiss.read_index(index_path)
            with open(chunks_path, 'r') as f:
                self.chunks = json.load(f)
            print(f"📂 Loaded vector store from {index_path}")
            return True
        return False

# ─────────────────────────────────────────────
# STEP 1: Load Document
# ─────────────────────────────────────────────
def load_faq(path="faq.txt"):
    with open(path) as f:
        text = f.read()
    # Split into chunks by Q&A pairs
    chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
    print(f"📄 Loaded {len(chunks)} chunks")
    return chunks

# ─────────────────────────────────────────────
# STEP 2: Extract Entities & Relations (LLM)
# ─────────────────────────────────────────────
def extract(chunk):
    prompt = f"""Extract entities and relations from this text.
Return ONLY valid JSON like:
{{"entities": [{{"name": "AI", "type": "CONCEPT"}}], "relations": [{{"source": "ML", "relation": "SUBSET_OF", "target": "AI"}}]}}

Text: {chunk}"""

    res = ai.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    text = res.choices[0].message.content.strip()
    # Clean markdown code blocks
    if "```" in text:
        text = text.split("```")[1].removeprefix("json").strip()
    try:
        return json.loads(text)
    except:
        return {"entities": [], "relations": []}

# ─────────────────────────────────────────────
# STEP 3: Store in Neo4j
# ─────────────────────────────────────────────
def store_graph(entities, relations):
    with db.session() as s:
        s.run("MATCH (n) DETACH DELETE n")  # Clear old data
        for e in entities:
            s.run("MERGE (n:Entity {name: $name}) SET n.type = $type", 
                  name=e["name"], type=e["type"])
        for r in relations:
            s.run("""
                MATCH (a:Entity {name: $src}), (b:Entity {name: $tgt})
                MERGE (a)-[:RELATES {type: $rel}]->(b)
            """, src=r["source"], rel=r["relation"], tgt=r["target"])
    print(f"💾 Stored {len(entities)} entities, {len(relations)} relations in Neo4j")

# ─────────────────────────────────────────────
# STEP 4: Search Knowledge Graph
# ─────────────────────────────────────────────
def search_graph(question):
    # Ask LLM to extract keywords
    res = ai.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": f'Extract keywords from this question as a JSON array: "{question}"'}],
        temperature=0
    )
    text = res.choices[0].message.content.strip()
    if "```" in text:
        text = text.split("```")[1].removeprefix("json").strip()
    keywords = json.loads(text)

    # Search Neo4j for matching entities + their connections
    results = []
    with db.session() as s:
        for kw in keywords:
            records = s.run("""
                MATCH (n:Entity) WHERE toLower(n.name) CONTAINS toLower($kw)
                OPTIONAL MATCH (n)-[r:RELATES]->(m)
                OPTIONAL MATCH (p)-[r2:RELATES]->(n)
                RETURN n.name AS entity, n.type AS type,
                       collect(DISTINCT {rel: r.type, target: m.name}) AS out,
                       collect(DISTINCT {rel: r2.type, source: p.name}) AS inc
            """, kw=kw)
            for rec in records:
                d = rec.data()
                info = f"{d['entity']} ({d['type']})"
                for o in d['out']:
                    if o['target']: info += f"\n  → {d['entity']} --{o['rel']}--> {o['target']}"
                for i in d['inc']:
                    if i['source']: info += f"\n  ← {i['source']} --{i['rel']}--> {d['entity']}"
                results.append(info)
    return "\n\n".join(results) if results else ""

# ─────────────────────────────────────────────
# STEP 5: Hybrid RAG Query
# ─────────────────────────────────────────────
def hybrid_search(question, vector_store, top_k=3):
    """Combine vector search and knowledge graph search"""
    
    # 1. Vector search for semantic similarity
    print(f"\n🔍 Vector Search:")
    vector_results = vector_store.search(question, top_k=top_k)
    vector_context = "\n\n".join([f"[Chunk {i+1}] {r['chunk']}" for i, r in enumerate(vector_results)])
    print(f"  Found {len(vector_results)} relevant chunks")
    
    # 2. Knowledge graph search for structured relationships
    print(f"\n🕸️  Knowledge Graph Search:")
    graph_context = search_graph(question)
    if graph_context:
        print(f"  Found graph relationships")
    else:
        print(f"  No graph relationships found")
    
    return vector_context, graph_context

def ask(question, vector_store):
    """Answer question using hybrid RAG"""
    vector_context, graph_context = hybrid_search(question, vector_store)
    
    # Combine both contexts
    combined_context = ""
    if vector_context:
        combined_context += f"=== SEMANTIC CONTEXT ===\n{vector_context}\n\n"
    if graph_context:
        combined_context += f"=== KNOWLEDGE GRAPH ===\n{graph_context}"
    
    if not combined_context.strip():
        return "I couldn't find relevant information to answer your question."
    
    # Generate answer using LLM
    res = ai.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": "Answer based on the provided context. Use both semantic context and knowledge graph relationships. Be concise and accurate."},
            {"role": "user", "content": f"Context:\n{combined_context}\n\nQuestion: {question}"}
        ],
        temperature=0.3
    )
    return res.choices[0].message.content

# ─────────────────────────────────────────────
# RUN THE PIPELINE
# ─────────────────────────────────────────────
if __name__ == "__main__":
    vector_store = VectorStore()
    
    # Try to load existing index
    if vector_store.load():
        print("✅ Loaded existing vector store")
    else:
        print("🚀 Building Hybrid RAG System...\n")
        
        # === BUILD PHASE ===
        chunks = load_faq()
        
        # 1. Build FAISS Vector Index
        print("\n📊 Building Vector Index...")
        vector_store.add_chunks(chunks)
        vector_store.save()
        
        # 2. Build Neo4j Knowledge Graph
        print("\n🕸️  Building Knowledge Graph...")
        all_entities, all_relations = [], []
        seen_e, seen_r = set(), set()

        for i, chunk in enumerate(chunks):
            print(f"  🧠 Extracting chunk {i+1}/{len(chunks)}...")
            data = extract(chunk)
            for e in data["entities"]:
                if e["name"] not in seen_e:
                    seen_e.add(e["name"])
                    all_entities.append(e)
            for r in data["relations"]:
                key = (r["source"], r["relation"], r["target"])
                if key not in seen_r:
                    seen_r.add(key)
                    all_relations.append(r)

        store_graph(all_entities, all_relations)
        print("\n✅ Hybrid RAG System ready!\n")

    # === QUERY PHASE ===
    print("\n" + "="*60)
    print("💬 HYBRID RAG - Ask anything! (type 'quit' to exit)")
    print("="*60 + "\n")
    
    while True:
        q = input("❓ Question: ").strip()
        if q.lower() in ["quit", "exit", "q"]: 
            break
        if q:
            print(f"\n💡 Answer:\n{ask(q, vector_store)}\n")
            print("-"*60 + "\n")

    db.close()
    print("👋 Goodbye!")
