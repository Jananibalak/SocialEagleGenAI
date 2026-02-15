"""
Web Search RAG - Complete Implementation
Demonstrates all prompt engineering techniques for Web Search RAG
"""

import json
from datetime import datetime
from typing import List, Dict, Any
import re


class WebSearchRAG:
    """
    A complete Web Search RAG system with advanced prompt engineering
    """
    
    def __init__(self, knowledge_cutoff="2025-01-31"):
        self.knowledge_cutoff = knowledge_cutoff
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        
    # ========== PROMPT TEMPLATES ==========
    
    QUERY_ANALYSIS_PROMPT = """
You are a query analyzer. Determine if this question requires web search.

User Query: {query}
Current Date: {current_date}
Knowledge Cutoff: {knowledge_cutoff}

Analyze:
1. Time Sensitivity (Does it ask about "latest", "current", "recent", "today"?)
2. Knowledge Cutoff (Could the answer have changed since {knowledge_cutoff}?)
3. Real-time Data (Stock prices, weather, news, sports scores?)
4. Verification Need (Facts that should be verified against current sources?)

Output JSON:
{{
  "needs_web_search": true/false,
  "reasoning": "explanation",
  "query_type": "current_events/real_time_data/recent_info/static_knowledge",
  "urgency": "high/medium/low"
}}

Think carefully and respond in JSON format only:
"""

    SEARCH_QUERY_OPTIMIZER = """
Convert the user's natural language query into optimized search queries.

User Query: {original_query}
Current Date: {current_date}

Generate 2-3 search queries that will find the best results:
- Query 1: Broad search
- Query 2: Specific/targeted search  
- Query 3: Alternative phrasing (if needed)

Include relevant keywords like:
- Time markers (2026, today, latest, recent)
- Specific entities (names, places, products)
- Context words (official, news, announcement)

Return as JSON array:
{{
  "queries": [
    "query 1 text",
    "query 2 text",
    "query 3 text"
  ]
}}

Generate:
"""

    WEB_RESULTS_PROCESSOR = """
You are processing web search results. Extract and organize relevant information.

User Query: {query}
Current Date: {current_date}

Web Search Results:
{search_results}

For each result, extract:
1. Relevance Score (0-10): How relevant to the query?
2. Freshness Score (0-10): How recent is the information?
3. Credibility Score (0-10): How trustworthy is the source?
4. Key Information: Main facts/data points
5. Publication Date: When was this published?

Return JSON array:
{{
  "processed_results": [
    {{
      "result_id": 1,
      "title": "result title",
      "source": "domain.com",
      "date": "YYYY-MM-DD",
      "relevance_score": 8,
      "freshness_score": 9,
      "credibility_score": 7,
      "key_information": ["fact 1", "fact 2"],
      "url": "full url"
    }}
  ]
}}

Process:
"""

    CREDIBILITY_EVALUATOR = """
Evaluate the credibility of this web source.

Source Domain: {domain}
Title: {title}
Publication Date: {date}
Content Snippet: {snippet}

Credibility Factors:
1. Domain Authority
   - Official sources (.gov, .edu, established organizations): 9-10
   - Major news outlets (NYTimes, BBC, Reuters): 7-8
   - Industry publications: 6-7
   - Blogs/personal sites: 3-5
   - Unknown domains: 1-3

2. Content Quality
   - Well-sourced, factual: +2
   - Opinion or editorial: -1
   - Clickbait/sensational: -2

3. Freshness (for current events)
   - Published today/yesterday: +2
   - Published this week: +1
   - Published this month: 0
   - Older than 1 month: -1

Return JSON:
{{
  "credibility_score": 7,
  "credibility_level": "high/medium/low",
  "reasoning": "explanation",
  "recommendation": "use/use_with_caution/avoid"
}}

Evaluate:
"""

    CONFLICT_RESOLVER = """
Multiple sources provide conflicting information. Resolve the conflict.

User Query: {query}

Conflicting Sources:
{conflicts}

Resolution Strategy:
1. Prioritize higher credibility sources
2. Prefer more recent information
3. Look for consensus among multiple sources
4. Consider if it's developing/breaking news

Return JSON:
{{
  "resolution": "the most accurate information",
  "confidence": "high/medium/low",
  "reasoning": "explanation of resolution",
  "caveat": "note any remaining uncertainty"
}}

Resolve:
"""

    FINAL_ANSWER_PROMPT = """
Generate a comprehensive answer using verified web search results.

User Question: {query}
Current Date: {current_date}

Verified Web Results:
{results}

Instructions:
1. Synthesize information from multiple sources
2. Prioritize more recent and credible sources
3. MANDATORY: Cite every claim with [Source #]
4. Include publication dates in citations
5. Note if sources conflict
6. Indicate confidence level
7. Mention if information is breaking/developing

Format your response as:

**Answer:**
[Your comprehensive answer with inline citations like [1], [2]]

**Sources:**
[1] Title - Domain (Date)
[2] Title - Domain (Date)

**Confidence:** High/Medium/Low
**Last Updated:** [Most recent source date]
**Notes:** [Any caveats or developing information]

Generate answer:
"""

    # ========== HELPER METHODS ==========
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Step 1: Analyze if query needs web search"""
        prompt = self.QUERY_ANALYSIS_PROMPT.format(
            query=query,
            current_date=self.current_date,
            knowledge_cutoff=self.knowledge_cutoff
        )
        
        # Simulating LLM call - in production, call actual LLM
        print("=" * 70)
        print("STEP 1: QUERY ANALYSIS")
        print("=" * 70)
        print(prompt)
        print("\n>>> Simulated Analysis Result:")
        
        # Example response
        result = {
            "needs_web_search": self._needs_web_search_heuristic(query),
            "reasoning": self._get_reasoning(query),
            "query_type": self._classify_query(query),
            "urgency": self._assess_urgency(query)
        }
        print(json.dumps(result, indent=2))
        return result
    
    def optimize_search_queries(self, query: str) -> List[str]:
        """Step 2: Create optimized search queries"""
        prompt = self.SEARCH_QUERY_OPTIMIZER.format(
            original_query=query,
            current_date=self.current_date
        )
        
        print("\n" + "=" * 70)
        print("STEP 2: SEARCH QUERY OPTIMIZATION")
        print("=" * 70)
        print(prompt)
        
        # Simulated optimization
        queries = self._generate_search_queries(query)
        print("\n>>> Optimized Queries:")
        for i, q in enumerate(queries, 1):
            print(f"  Query {i}: {q}")
        
        return queries
    
    def process_search_results(self, query: str, search_results: List[Dict]) -> List[Dict]:
        """Step 3: Process and score web search results"""
        
        results_text = self._format_results_for_prompt(search_results)
        
        prompt = self.WEB_RESULTS_PROCESSOR.format(
            query=query,
            current_date=self.current_date,
            search_results=results_text
        )
        
        print("\n" + "=" * 70)
        print("STEP 3: PROCESS SEARCH RESULTS")
        print("=" * 70)
        print(prompt[:500] + "...\n")
        
        # Simulated processing
        processed = self._process_results(search_results)
        print(">>> Processed Results:")
        for r in processed:
            print(f"\n  [{r['result_id']}] {r['title']}")
            print(f"      Relevance: {r['relevance_score']}/10 | "
                  f"Freshness: {r['freshness_score']}/10 | "
                  f"Credibility: {r['credibility_score']}/10")
            print(f"      Source: {r['source']} ({r['date']})")
        
        return processed
    
    def evaluate_credibility(self, result: Dict) -> Dict:
        """Step 4: Evaluate source credibility"""
        prompt = self.CREDIBILITY_EVALUATOR.format(
            domain=result['domain'],
            title=result['title'],
            date=result.get('date', 'Unknown'),
            snippet=result.get('snippet', '')[:200]
        )
        
        print("\n" + "=" * 70)
        print(f"STEP 4: CREDIBILITY EVALUATION - {result['domain']}")
        print("=" * 70)
        print(prompt[:400] + "...\n")
        
        # Simulated evaluation
        credibility = self._evaluate_source_credibility(result['domain'])
        print(">>> Credibility Assessment:")
        print(json.dumps(credibility, indent=2))
        
        return credibility
    
    def resolve_conflicts(self, query: str, conflicting_results: List[Dict]) -> Dict:
        """Step 5: Resolve conflicting information"""
        
        conflicts_text = self._format_conflicts(conflicting_results)
        
        prompt = self.CONFLICT_RESOLVER.format(
            query=query,
            conflicts=conflicts_text
        )
        
        print("\n" + "=" * 70)
        print("STEP 5: CONFLICT RESOLUTION")
        print("=" * 70)
        print(prompt)
        
        # Simulated resolution
        resolution = {
            "resolution": self._resolve_conflict(conflicting_results),
            "confidence": "medium",
            "reasoning": "Prioritizing most recent official source",
            "caveat": "Information is still developing"
        }
        print("\n>>> Resolution:")
        print(json.dumps(resolution, indent=2))
        
        return resolution
    
    def generate_final_answer(self, query: str, processed_results: List[Dict]) -> str:
        """Step 6: Generate final answer with citations"""
        
        results_text = self._format_results_for_answer(processed_results)
        
        prompt = self.FINAL_ANSWER_PROMPT.format(
            query=query,
            current_date=self.current_date,
            results=results_text
        )
        
        print("\n" + "=" * 70)
        print("STEP 6: FINAL ANSWER GENERATION")
        print("=" * 70)
        print(prompt[:500] + "...\n")
        
        # Simulated answer
        answer = self._generate_answer(query, processed_results)
        print(">>> FINAL ANSWER:")
        print(answer)
        
        return answer
    
    # ========== SIMULATION HELPERS ==========
    
    def _needs_web_search_heuristic(self, query: str) -> bool:
        """Simple heuristic to determine if web search is needed"""
        time_keywords = ['latest', 'current', 'recent', 'today', 'now', '2026', 'this year']
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in time_keywords)
    
    def _get_reasoning(self, query: str) -> str:
        """Generate reasoning for web search decision"""
        if self._needs_web_search_heuristic(query):
            return "Query contains time-sensitive keywords requiring current information"
        return "Query can likely be answered with existing knowledge"
    
    def _classify_query(self, query: str) -> str:
        """Classify the type of query"""
        query_lower = query.lower()
        if any(word in query_lower for word in ['price', 'weather', 'score', 'stock']):
            return "real_time_data"
        elif any(word in query_lower for word in ['news', 'announced', 'released', 'happened']):
            return "current_events"
        elif any(word in query_lower for word in ['latest', 'recent', 'new']):
            return "recent_info"
        return "static_knowledge"
    
    def _assess_urgency(self, query: str) -> str:
        """Assess urgency of the query"""
        query_lower = query.lower()
        if any(word in query_lower for word in ['now', 'today', 'current', 'live']):
            return "high"
        elif any(word in query_lower for word in ['recent', 'latest', 'this week']):
            return "medium"
        return "low"
    
    def _generate_search_queries(self, query: str) -> List[str]:
        """Generate optimized search queries"""
        # Simple query optimization
        base_query = query
        queries = [
            f"{base_query} {self.current_date.split('-')[0]}",  # Add year
            f"{base_query} latest news",  # Add 'latest'
            f"{base_query} official announcement"  # Add 'official'
        ]
        return queries[:3]
    
    def _format_results_for_prompt(self, results: List[Dict]) -> str:
        """Format search results for prompt"""
        formatted = []
        for i, r in enumerate(results, 1):
            formatted.append(f"""
Result #{i}:
Title: {r['title']}
Source: {r['domain']}
Date: {r.get('date', 'Unknown')}
Snippet: {r.get('snippet', 'No snippet available')}
URL: {r.get('url', 'No URL')}
""")
        return "\n".join(formatted)
    
    def _process_results(self, results: List[Dict]) -> List[Dict]:
        """Process and score results"""
        processed = []
        for i, r in enumerate(results, 1):
            processed.append({
                "result_id": i,
                "title": r['title'],
                "source": r['domain'],
                "date": r.get('date', 'Unknown'),
                "relevance_score": 8,  # Simulated score
                "freshness_score": self._calculate_freshness(r.get('date')),
                "credibility_score": self._get_domain_credibility(r['domain']),
                "key_information": [r.get('snippet', '')[:100]],
                "url": r.get('url', '')
            })
        return processed
    
    def _calculate_freshness(self, date_str: str) -> int:
        """Calculate freshness score based on date"""
        if not date_str or date_str == 'Unknown':
            return 5
        # Simple simulation
        if '2026' in date_str:
            return 10
        elif '2025' in date_str:
            return 7
        return 4
    
    def _get_domain_credibility(self, domain: str) -> int:
        """Get credibility score for domain"""
        if any(ext in domain for ext in ['.gov', '.edu']):
            return 10
        elif any(site in domain for site in ['bbc', 'reuters', 'nytimes', 'wsj']):
            return 9
        elif any(site in domain for site in ['techcrunch', 'theverge', 'wired']):
            return 7
        return 6
    
    def _evaluate_source_credibility(self, domain: str) -> Dict:
        """Evaluate source credibility"""
        score = self._get_domain_credibility(domain)
        if score >= 8:
            level = "high"
            rec = "use"
        elif score >= 6:
            level = "medium"
            rec = "use_with_caution"
        else:
            level = "low"
            rec = "avoid"
        
        return {
            "credibility_score": score,
            "credibility_level": level,
            "reasoning": f"Domain {domain} has established reputation",
            "recommendation": rec
        }
    
    def _format_conflicts(self, results: List[Dict]) -> str:
        """Format conflicting results"""
        formatted = []
        for i, r in enumerate(results, 1):
            formatted.append(f"Source {chr(64+i)} ({r['domain']}, {r.get('date', 'Unknown')}): {r.get('snippet', 'N/A')}")
        return "\n".join(formatted)
    
    def _resolve_conflict(self, results: List[Dict]) -> str:
        """Resolve conflicts between sources"""
        # Sort by credibility and date
        sorted_results = sorted(results, 
                               key=lambda x: (self._get_domain_credibility(x['domain']), 
                                            x.get('date', '')), 
                               reverse=True)
        return sorted_results[0].get('snippet', 'Unable to resolve')
    
    def _format_results_for_answer(self, results: List[Dict]) -> str:
        """Format processed results for final answer"""
        formatted = []
        for r in results:
            formatted.append(f"""
[{r['result_id']}] {r['title']}
    Source: {r['source']} ({r['date']})
    Relevance: {r['relevance_score']}/10
    Key Info: {', '.join(r['key_information'])}
""")
        return "\n".join(formatted)
    
    def _generate_answer(self, query: str, results: List[Dict]) -> str:
        """Generate final answer (simulated)"""
        # Sort by combined score
        sorted_results = sorted(results, 
                               key=lambda x: (x['relevance_score'] + 
                                            x['freshness_score'] + 
                                            x['credibility_score']) / 3,
                               reverse=True)
        
        answer = f"""**Answer:**
Based on recent web sources, {query.split('?')[0].lower()}. According to {sorted_results[0]['source']} [1], {sorted_results[0]['key_information'][0]}. This is corroborated by {sorted_results[1]['source']} [2], published on {sorted_results[1]['date']}.

**Sources:**
[1] {sorted_results[0]['title']} - {sorted_results[0]['source']} ({sorted_results[0]['date']})
[2] {sorted_results[1]['title']} - {sorted_results[1]['source']} ({sorted_results[1]['date']})

**Confidence:** High
**Last Updated:** {sorted_results[0]['date']}
**Notes:** Information is current as of {self.current_date}. For real-time updates, check the cited sources directly.
"""
        return answer


# ========== DEMONSTRATION ==========

def main():
    """Demonstrate the complete Web Search RAG workflow"""
    
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "WEB SEARCH RAG - COMPLETE DEMO" + " " * 23 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # Initialize the system
    rag = WebSearchRAG()
    
    # Example query
    query = "What is the latest news about AI regulations in 2026?"
    print(f"\n📝 User Query: {query}\n")
    
    # Step 1: Analyze query
    analysis = rag.analyze_query(query)
    
    if not analysis['needs_web_search']:
        print("\n⚠️  Web search not needed. Answering from knowledge base...")
        return
    
    # Step 2: Optimize search queries
    search_queries = rag.optimize_search_queries(query)
    
    # Step 3: Simulate web search results
    print("\n" + "=" * 70)
    print("SIMULATING WEB SEARCH...")
    print("=" * 70)
    
    mock_results = [
        {
            "title": "EU Passes Comprehensive AI Act in February 2026",
            "domain": "bbc.com",
            "date": "2026-02-05",
            "snippet": "The European Union has finalized groundbreaking AI regulations...",
            "url": "https://bbc.com/news/ai-act-2026"
        },
        {
            "title": "US Proposes New AI Safety Framework",
            "domain": "reuters.com",
            "date": "2026-02-03",
            "snippet": "The Biden administration announced new guidelines for AI development...",
            "url": "https://reuters.com/ai-safety-2026"
        },
        {
            "title": "China Updates AI Governance Rules",
            "domain": "techcrunch.com",
            "date": "2026-01-28",
            "snippet": "China's Cyberspace Administration released updated AI regulations...",
            "url": "https://techcrunch.com/china-ai-rules"
        }
    ]
    
    # Step 4: Process results
    processed_results = rag.process_search_results(query, mock_results)
    
    # Step 5: Evaluate credibility (for first result as example)
    credibility = rag.evaluate_credibility(mock_results[0])
    
    # Step 6: Check for conflicts (simulated)
    # In real scenario, this would detect conflicting information
    # For demo, we'll skip if no conflicts
    
    # Step 7: Generate final answer
    final_answer = rag.generate_final_answer(query, processed_results)
    
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " " * 24 + "WORKFLOW COMPLETE" + " " * 27 + "║")
    print("╚" + "=" * 68 + "╝")


if __name__ == "__main__":
    main()
