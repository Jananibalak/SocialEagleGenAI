"""
Utility functions for the RAG application
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

def load_env_vars() -> Dict[str, str]:
    """
    Load environment variables from .env file
    Returns:
        Dictionary with API keys and configurations
    """
    load_dotenv()
    
    return {
        'openai_api_key': os.getenv('OPENAI_API_KEY', ''),
        'serp_api_key': os.getenv('SERPAPI_KEY', ''),
        'neo4j_uri': os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        'neo4j_user': os.getenv('NEO4J_USER', 'neo4j'),
        'neo4j_password': os.getenv('NEO4J_PASSWORD', ''),
        'chunk_size': int(os.getenv('CHUNK_SIZE', '1000')),
        'chunk_overlap': int(os.getenv('CHUNK_OVERLAP', '200'))
    }

def test_neo4j_connection(uri: str, user: str, password: str) -> bool:
    """
    Test Neo4j database connection
    Args:
        uri: Neo4j URI
        user: Neo4j username
        password: Neo4j password
    Returns:
        True if connection successful, False otherwise
    """
    try:
        from neo4j import GraphDatabase
        
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        driver.close()
        print("✅ Neo4j connection successful")
        return True
    except Exception as e:
        print(f"❌ Neo4j connection failed: {str(e)}")
        return False

def test_openai_connection(api_key: str) -> bool:
    """
    Test OpenAI API connection
    Args:
        api_key: OpenAI API key
    Returns:
        True if connection successful, False otherwise
    """
    try:
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(
            temperature=0,
            model_name="openai/gpt-4o-mini",
            openai_api_key=api_key
        )
        
        # Simple test query
        response = llm.predict("Say 'test successful'")
        print("✅ OpenAI connection successful")
        print(f"Response: {response}")
        return True
    except Exception as e:
        print(f"❌ OpenAI connection failed: {str(e)}")
        return False

def test_serp_api(api_key: str) -> bool:
    """
    Test SerpAPI connection
    Args:
        api_key: SerpAPI key
    Returns:
        True if connection successful, False otherwise
    """
    try:
        import requests
        
        url = "https://serpapi.com/search"
        params = {
            "q": "test query",
            "api_key": api_key,
            "engine": "google"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        print("✅ SerpAPI connection successful")
        print(f"Search credits remaining: {response.json().get('search_metadata', {}).get('total_time_taken', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ SerpAPI connection failed: {str(e)}")
        return False

def validate_pdf_size(file_path: str, max_size_kb: int = 100) -> bool:
    """
    Validate PDF file size
    Args:
        file_path: Path to PDF file
        max_size_kb: Maximum allowed size in KB
    Returns:
        True if valid, False otherwise
    """
    try:
        file_size = os.path.getsize(file_path)
        file_size_kb = file_size / 1024
        
        if file_size_kb > max_size_kb:
            print(f"❌ File size ({file_size_kb:.2f}KB) exceeds {max_size_kb}KB limit")
            return False
        
        print(f"✅ File size ({file_size_kb:.2f}KB) is within limit")
        return True
    except Exception as e:
        print(f"❌ Error checking file size: {str(e)}")
        return False

def get_sample_pdf_url() -> str:
    """
    Return a sample PDF URL for testing
    Returns:
        URL string
    """
    return "https://arxiv.org/pdf/1706.03762.pdf"  # Attention is All You Need paper

def get_sample_web_url() -> str:
    """
    Return a sample web URL for testing
    Returns:
        URL string
    """
    return "https://en.wikipedia.org/wiki/Retrieval-augmented_generation"

def print_system_info():
    """
    Print system information for debugging
    """
    import sys
    import platform
    
    print("\n" + "="*50)
    print("SYSTEM INFORMATION")
    print("="*50)
    print(f"Python Version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Machine: {platform.machine()}")
    print("="*50 + "\n")

def run_all_tests():
    """
    Run all connection tests
    """
    print_system_info()
    
    print("Loading environment variables...")
    env_vars = load_env_vars()
    
    print("\nRunning connection tests...\n")
    
    # Test OpenAI
    if env_vars['openai_api_key']:
        test_openai_connection(env_vars['openai_api_key'])
    else:
        print("⚠️  OpenAI API key not found in environment")
    
    print()
    
    # Test SerpAPI
    if env_vars['serp_api_key']:
        test_serp_api(env_vars['serp_api_key'])
    else:
        print("⚠️  SerpAPI key not found in environment")
    
    print()
    
    # Test Neo4j
    if env_vars['neo4j_password']:
        test_neo4j_connection(
            env_vars['neo4j_uri'],
            env_vars['neo4j_user'],
            env_vars['neo4j_password']
        )
    else:
        print("⚠️  Neo4j password not found in environment")
    
    print("\n" + "="*50)
    print("Tests complete!")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_all_tests()
