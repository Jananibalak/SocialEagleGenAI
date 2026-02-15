"""
Test script for RAG application
Run this to verify your setup before using the Streamlit app
"""

import sys
import os

def check_imports():
    """Check if all required packages are installed"""
    print("\n" + "="*60)
    print("CHECKING PACKAGE IMPORTS")
    print("="*60 + "\n")
    
    packages = [
        ('streamlit', 'Streamlit'),
        ('langchain', 'LangChain'),
        ('langchain_openai', 'LangChain OpenAI'),
        ('langchain_community', 'LangChain Community'),
        ('faiss', 'FAISS'),
        ('neo4j', 'Neo4j Driver'),
        ('pypdf', 'PyPDF'),
        ('bs4', 'BeautifulSoup4'),
        ('requests', 'Requests'),
        ('dotenv', 'Python-dotenv'),
    ]
    
    success_count = 0
    fail_count = 0
    
    for package, name in packages:
        try:
            __import__(package)
            print(f"✅ {name:25s} - OK")
            success_count += 1
        except ImportError as e:
            print(f"❌ {name:25s} - MISSING")
            fail_count += 1
    
    print(f"\n{success_count}/{len(packages)} packages installed successfully")
    
    if fail_count > 0:
        print(f"\n⚠️  {fail_count} package(s) missing. Run: pip install -r requirements.txt")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists"""
    print("\n" + "="*60)
    print("CHECKING ENVIRONMENT CONFIGURATION")
    print("="*60 + "\n")
    
    if os.path.exists('.env'):
        print("✅ .env file found")
        
        from dotenv import load_dotenv
        load_dotenv()
        
        keys = [
            'OPENAI_API_KEY',
            'SERPAPI_KEY',
            'NEO4J_PASSWORD'
        ]
        
        for key in keys:
            value = os.getenv(key)
            if value:
                masked = value[:8] + '...' if len(value) > 8 else '***'
                print(f"✅ {key:20s} - Set ({masked})")
            else:
                print(f"⚠️  {key:20s} - Not set")
        
        return True
    else:
        print("⚠️  .env file not found")
        print("   Create one using .env.example as template")
        print("   Or enter API keys directly in the Streamlit interface")
        return False

def test_minimal_rag():
    """Test basic RAG functionality"""
    print("\n" + "="*60)
    print("TESTING MINIMAL RAG SETUP")
    print("="*60 + "\n")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        openai_key = os.getenv('OPENAI_API_KEY')
        
        if not openai_key:
            print("⚠️  OPENAI_API_KEY not set, skipping functional test")
            return False
        
        print("Creating sample document...")
        from langchain.schema import Document
        
        docs = [
            Document(page_content="The capital of France is Paris.", metadata={"source": "test"}),
            Document(page_content="Python is a popular programming language.", metadata={"source": "test"}),
        ]
        
        print("✅ Sample documents created")
        
        print("\nCreating embeddings...")
        from langchain_openai import OpenAIEmbeddings
        embeddings = OpenAIEmbeddings(openai_api_key=openai_key)
        print("✅ Embeddings initialized")
        
        print("\nCreating FAISS vector store...")
        from langchain_community.vectorstores import FAISS
        vector_store = FAISS.from_documents(docs, embeddings)
        print("✅ Vector store created")
        
        print("\nTesting similarity search...")
        results = vector_store.similarity_search("What is the capital of France?", k=1)
        print(f"✅ Search result: {results[0].page_content}")
        
        print("\nTesting with LLM...")
        from langchain_openai import ChatOpenAI
        from langchain.chains import RetrievalQA
        
        llm = ChatOpenAI(temperature=0, model_name="openai/gpt-4o-mini", openai_api_key=openai_key)
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever(),
        )
        
        result = qa_chain({"query": "What is the capital of France?"})
        print(f"✅ QA Answer: {result['result']}")
        
        print("\n✅ All RAG components working!")
        return True
        
    except Exception as e:
        print(f"\n❌ RAG test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_neo4j():
    """Test Neo4j connection"""
    print("\n" + "="*60)
    print("TESTING NEO4J CONNECTION")
    print("="*60 + "\n")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        from neo4j import GraphDatabase
        
        uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        user = os.getenv('NEO4J_USER', 'neo4j')
        password = os.getenv('NEO4J_PASSWORD')
        
        if not password:
            print("⚠️  NEO4J_PASSWORD not set, skipping Neo4j test")
            return False
        
        print(f"Connecting to {uri}...")
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # Test connection
        driver.verify_connectivity()
        print("✅ Connected to Neo4j")
        
        # Test query
        with driver.session() as session:
            result = session.run("RETURN 'Hello Neo4j!' as message")
            record = result.single()
            print(f"✅ Test query result: {record['message']}")
        
        driver.close()
        print("✅ Neo4j test complete")
        return True
        
    except Exception as e:
        print(f"❌ Neo4j test failed: {str(e)}")
        print("\nMake sure Neo4j is running:")
        print("  docker-compose up -d")
        print("  OR")
        print("  Start Neo4j Desktop")
        return False

def test_serp_api():
    """Test SerpAPI"""
    print("\n" + "="*60)
    print("TESTING SERPAPI")
    print("="*60 + "\n")
    
    try:
        from dotenv import load_dotenv
        import requests
        load_dotenv()
        
        api_key = os.getenv('SERPAPI_KEY')
        
        if not api_key:
            print("⚠️  SERPAPI_KEY not set, skipping SerpAPI test")
            return False
        
        print("Testing web search...")
        url = "https://serpapi.com/search"
        params = {
            "q": "python programming",
            "api_key": api_key,
            "engine": "google",
            "num": 1
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'organic_results' in data and len(data['organic_results']) > 0:
            result = data['organic_results'][0]
            print(f"✅ Search successful!")
            print(f"   Title: {result.get('title', 'N/A')}")
            print(f"   Snippet: {result.get('snippet', 'N/A')[:100]}...")
        
        # Check remaining searches
        if 'search_metadata' in data:
            print(f"\n✅ SerpAPI test complete")
        
        return True
        
    except Exception as e:
        print(f"❌ SerpAPI test failed: {str(e)}")
        print("\nGet a free API key at: https://serpapi.com/")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("RAG APPLICATION SETUP VERIFICATION")
    print("="*60)
    
    # Check Python version
    print(f"\nPython version: {sys.version}")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return
    
    # Run tests
    tests = [
        ("Package Imports", check_imports),
        ("Environment File", check_env_file),
        ("Basic RAG", test_minimal_rag),
        ("Neo4j", test_neo4j),
        ("SerpAPI", test_serp_api),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} test crashed: {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60 + "\n")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20s} - {status}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! You're ready to run the app:")
        print("   streamlit run app.py")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("   Fix the issues before running the app.")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
