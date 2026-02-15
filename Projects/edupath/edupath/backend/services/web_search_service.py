from serpapi import GoogleSearch
import os
from typing import List, Dict

class WebSearchService:
    """
    Web search using SerpAPI when local knowledge insufficient
    """
    
    def __init__(self):
        self.api_key = os.getenv("SERP_API_KEY")
        
        if not self.api_key:
            print("⚠️ SERP_API_KEY not set in .env - web search disabled")
    
    def search(self, query: str, num_results: int = 3) -> List[Dict]:
        """
        Search the web using SerpAPI
        
        Returns:
            List of search results with title, snippet, link
        """
        
        if not self.api_key:
            return []
        
        try:
            print(f"🌐 Searching web for: {query}")
            
            params = {
                "q": query,
                "api_key": self.api_key,
                "num": num_results,
                "engine": "google"
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            # Extract organic results
            organic_results = results.get("organic_results", [])
            
            formatted_results = []
            for result in organic_results[:num_results]:
                formatted_results.append({
                    'title': result.get('title', ''),
                    'snippet': result.get('snippet', ''),
                    'link': result.get('link', ''),
                    'source': 'web_search'
                })
            
            if formatted_results:
                print(f"✅ Found {len(formatted_results)} web results")
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Web search error: {e}")
            return []
    
    def search_and_format_context(self, query: str) -> str:
        """
        Search and format results as context string
        """
        results = self.search(query, num_results=3)
        
        if not results:
            return ""
        
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(
                f"[Web Source {i}: {result['title']}]\n{result['snippet']}\n"
            )
        
        return "\n".join(context_parts)