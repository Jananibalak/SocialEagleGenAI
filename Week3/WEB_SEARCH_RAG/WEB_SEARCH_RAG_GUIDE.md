# WEB SEARCH RAG - COMPLETE PROMPT ENGINEERING GUIDE

## Table of Contents
1. [Overview](#overview)
2. [Core Prompt Components](#core-prompt-components)
3. [6-Step Workflow](#6-step-workflow)
4. [Advanced Prompt Patterns](#advanced-prompt-patterns)
5. [Best Practices](#best-practices)
6. [Common Pitfalls](#common-pitfalls)
7. [Production Checklist](#production-checklist)

---

## Overview

Web Search RAG extends traditional RAG by incorporating real-time web search to answer queries requiring current information beyond the LLM's knowledge cutoff.

**When to Use Web Search RAG:**
- ✅ Time-sensitive queries (stocks, weather, news)
- ✅ Recent events (announcements, releases)
- ✅ Fact-checking current claims
- ✅ Queries about 2025-2026 events
- ❌ Historical facts
- ❌ General knowledge questions
- ❌ Mathematical computations

---

## Core Prompt Components

Every Web Search RAG prompt should include:

### 1. Context Information
```
User Query: {query}
Current Date: {current_date}
Knowledge Cutoff: {knowledge_cutoff}
```

### 2. Clear Instructions
```
Task: [What you want the LLM to do]

Instructions:
1. [Step 1]
2. [Step 2]
3. [Step 3]
```

### 3. Output Format Specification
```
Return ONLY valid JSON:
{
  "field1": "value",
  "field2": "value"
}

OR

Format:
**Section 1:**
[Content]

**Section 2:**
[Content]
```

### 4. Evaluation Criteria
```
Scoring:
- Relevance (0-10): How well does it match?
- Credibility (0-10): How trustworthy?
- Freshness (0-10): How recent?
```

### 5. Edge Case Handling
```
If information is conflicting: [What to do]
If sources are low quality: [What to do]
If no results found: [What to do]
```

---

## 6-Step Workflow

### STEP 1: Query Analysis

**Purpose:** Decide if web search is needed

**Prompt Template:**
```
You are a query analyzer. Determine if this question requires web search.

User Query: {query}
Current Date: {current_date}
Knowledge Cutoff: {knowledge_cutoff}

Analyze:
1. Time Sensitivity - Does it ask about "latest", "current", "recent"?
2. Knowledge Cutoff - Could answer have changed since {knowledge_cutoff}?
3. Real-time Data - Stock prices, weather, news, sports scores?
4. Verification Need - Should facts be verified against current sources?

Output JSON:
{
  "needs_web_search": true/false,
  "reasoning": "explanation",
  "query_type": "current_events/real_time_data/recent_info/static_knowledge",
  "urgency": "high/medium/low"
}
```

**Key Techniques:**
- Always include current date
- Mention knowledge cutoff explicitly
- Provide clear decision criteria
- Request structured JSON output
- Ask for reasoning (improves accuracy)

---

### STEP 2: Search Query Optimization

**Purpose:** Convert natural language to effective search queries

**Prompt Template:**
```
Convert the user's natural language query into optimized search queries.

User Query: {original_query}
Current Date: {current_date}

Generate 2-3 search queries that will find the best results:
- Query 1: Broad search
- Query 2: Specific/targeted search
- Query 3: Alternative phrasing (if needed)

Include relevant keywords:
- Time markers (2026, today, latest, recent)
- Specific entities (names, places, products)
- Context words (official, news, announcement)

Return as JSON:
{
  "queries": ["query 1", "query 2", "query 3"]
}
```

**Key Techniques:**
- Request 2-3 variations (not just 1)
- Provide keyword guidance
- Include current year for time-sensitive queries
- Keep queries concise (5-10 words optimal)
- Add context words ("official", "news", "latest")

**Examples:**

| User Query | Optimized Search Queries |
|------------|-------------------------|
| "What's the latest on AI regulations?" | 1. "AI regulations 2026 latest news"<br>2. "artificial intelligence policy February 2026"<br>3. "AI governance announcements 2026" |
| "Who won the election?" | 1. "election results 2026 winner"<br>2. "2026 election official results"<br>3. "election winner announced 2026" |

---

### STEP 3: Result Processing

**Purpose:** Extract and structure information from raw search results

**Prompt Template:**
```
Process web search results and extract relevant information.

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
{
  "processed_results": [
    {
      "result_id": 1,
      "title": "result title",
      "source": "domain.com",
      "date": "YYYY-MM-DD",
      "relevance_score": 8,
      "freshness_score": 9,
      "credibility_score": 7,
      "key_information": ["fact 1", "fact 2"],
      "url": "full url"
    }
  ]
}
```

**Key Techniques:**
- Multi-dimensional scoring (not just relevance)
- Extract publication dates explicitly
- Identify key information separately from full text
- Structure output for easy processing
- Include result IDs for reference

---

### STEP 4: Credibility Evaluation

**Purpose:** Assess trustworthiness of sources

**Prompt Template:**
```
Evaluate the credibility of this web source.

Source Domain: {domain}
Title: {title}
Publication Date: {date}
Content Snippet: {snippet}

Credibility Factors:
1. Domain Authority
   - Official sources (.gov, .edu, organizations): 9-10
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
   - This week: +1
   - This month: 0
   - Older than 1 month: -1

Return JSON:
{
  "credibility_score": 7,
  "credibility_level": "high/medium/low",
  "reasoning": "explanation",
  "recommendation": "use/use_with_caution/avoid"
}
```

**Credibility Scoring Guide:**

| Domain Type | Base Score | Examples |
|------------|------------|----------|
| Government/Education | 9-10 | .gov, .edu, WHO, UN |
| Major News Outlets | 7-8 | NYTimes, BBC, Reuters, WSJ |
| Industry Publications | 6-7 | TechCrunch, Wired, ArsTechnica |
| General Blogs | 3-5 | Medium, personal blogs |
| Unknown/Spam | 1-2 | Unknown domains |

**Key Techniques:**
- Provide explicit scoring rubrics
- Consider multiple factors (authority + quality + freshness)
- Give clear recommendations (use/caution/avoid)
- Adjust for context (blog may be credible for personal experiences)

---

### STEP 5: Conflict Resolution

**Purpose:** Handle contradictory information from multiple sources

**Prompt Template:**
```
Multiple sources provide conflicting information. Resolve the conflict.

User Query: {query}

Conflicting Sources:
Source A ({source_a_name}, {date_a}): {claim_a}
Source B ({source_b_name}, {date_b}): {claim_b}
Source C ({source_c_name}, {date_c}): {claim_c}

Resolution Strategy:
1. Prioritize higher credibility sources
2. Prefer more recent information (for developing news)
3. Look for consensus among multiple sources
4. Consider if it's breaking/developing news

Return JSON:
{
  "resolution": "the most accurate information",
  "confidence": "high/medium/low",
  "reasoning": "explanation of resolution",
  "caveat": "note any remaining uncertainty"
}
```

**Resolution Priority:**
1. **Official sources** beat news
2. **Recent sources** beat old (for current events)
3. **Consensus** beats individual claims
4. **Original sources** beat secondary reporting

**Key Techniques:**
- Present all conflicting claims explicitly
- Include source metadata (date, credibility)
- Request reasoning for resolution
- Always include confidence level
- Add caveats for uncertainty

---

### STEP 6: Answer Generation

**Purpose:** Synthesize final answer with proper citations

**Prompt Template:**
```
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

Format:
**Answer:**
[Your comprehensive answer with inline citations like [1], [2]]

**Sources:**
[1] Title - Domain (Date)
[2] Title - Domain (Date)

**Confidence:** High/Medium/Low
**Last Updated:** [Most recent source date]
**Notes:** [Any caveats, conflicts, or developing information]
```

**Citation Best Practices:**

✅ **Good Citations:**
```
The EU passed the AI Act on February 5, 2026 [1], marking a significant 
regulatory milestone. According to Reuters [2], this came after three years 
of negotiations.
```

❌ **Bad Citations:**
```
The EU passed an AI act. There were negotiations.
[No sources cited at all]
```

**Key Techniques:**
- **Mandatory inline citations** - use [1], [2] format
- **Include publication dates** - shows freshness
- **Multi-source synthesis** - don't rely on single source
- **Confidence indicators** - be honest about uncertainty
- **Caveat notes** - mention conflicts or developing stories

---

## Advanced Prompt Patterns

### Pattern 1: Time-Sensitive Queries

**Use For:** Stock prices, weather, breaking news, sports scores

**Special Instructions:**
```
Time-Sensitive Content Guidelines:
1. Lead with MOST RECENT information
2. Include timestamps prominently (e.g., "As of 2:30 PM EST...")
3. Flag if information is "breaking" or "developing"
4. Warn if sources are >24 hours old for breaking news
5. Note different update times across sources

Format:
**Latest Information (as of {most_recent_source_time}):**
[Answer with explicit time references]

⚠️ Update Frequency: This information changes rapidly. 
   Last checked: {current_time}
```

### Pattern 2: Multi-Perspective Synthesis

**Use For:** Controversial topics, policy debates, complex issues

**Special Instructions:**
```
Multi-Perspective Analysis:
1. Identify main narrative from each perspective
2. Note where perspectives agree vs. diverge
3. Highlight biases or conflicts of interest
4. Synthesize balanced view

Format:
**Consensus Points:** [Where sources agree]
**Divergent Perspectives:**
- Official view: [summary]
- Media coverage: [summary]
- Expert opinion: [summary]

**Analysis:** [Balanced synthesis]
```

### Pattern 3: Fact-Checking

**Use For:** Verifying claims, debunking misinformation

**Special Instructions:**
```
Fact-Check Framework:
1. VERIFY: Find original source
2. CORROBORATE: Multiple independent sources confirm?
3. CONTEXT: Claim missing important context?
4. CREDIBILITY: Sources authoritative?
5. RECENCY: Information current or outdated?

Verdict: TRUE/MOSTLY TRUE/MIXED/MOSTLY FALSE/FALSE/UNVERIFIABLE

Include:
- Supporting evidence
- Contradicting evidence
- Missing context
```

### Pattern 4: Comparison Queries

**Use For:** Product comparisons, service alternatives

**Special Instructions:**
```
Comparison Format:
| Criteria | Item A | Item B | Item C |
|----------|--------|--------|--------|
| Price | $X [1] | $Y [2] | $Z [3] |
| Rating | X/5 ⭐ | Y/5 ⭐ | Z/5 ⭐ |

Best For:
- Item A: [specific use case]
- Item B: [specific use case]

⚠️ Prices verified as of {date}. May vary by region.
```

---

## Best Practices

### DO ✅

1. **Always Include Context**
   - Current date
   - Knowledge cutoff
   - User's intent

2. **Request Structured Output**
   - Use JSON for processing
   - Specify exact format
   - Include examples

3. **Multi-Step Processing**
   - Analyze → Search → Evaluate → Generate
   - Don't skip evaluation steps
   - Quality over speed

4. **Explicit Citations**
   - Every claim must be cited
   - Include publication dates
   - Link to sources

5. **Confidence Indicators**
   - High/Medium/Low confidence
   - Note uncertainties
   - Flag developing stories

6. **Error Handling**
   - What if no results?
   - What if sources conflict?
   - What if low credibility?

### DON'T ❌

1. **Skip Query Analysis**
   - Don't search for static knowledge
   - Wastes API calls
   - Slower responses

2. **Use Single Source**
   - Always cross-reference
   - Risk of bias
   - May miss important info

3. **Ignore Dates**
   - Date crucial for freshness
   - Old info may be wrong
   - User needs to know recency

4. **Trust All Sources Equally**
   - Evaluate credibility
   - Prioritize authoritative sources
   - Flag questionable content

5. **Generate Without Context**
   - Always provide sources to LLM
   - Don't rely on LLM's knowledge
   - Use retrieved context

6. **Forget Edge Cases**
   - Handle conflicts
   - Deal with no results
   - Manage API failures

---

## Common Pitfalls

### Pitfall 1: Over-Searching
**Problem:** Searching when existing knowledge is sufficient

**Solution:**
```python
# Add query analysis step
analysis = analyze_query(query)
if not analysis['needs_web_search']:
    return answer_from_knowledge(query)
```

### Pitfall 2: Poor Query Optimization
**Problem:** Using natural language directly in search

**Solution:**
```python
# Bad
search("What are the latest developments in AI?")

# Good
search("AI developments 2026 latest")
search("artificial intelligence news February 2026")
```

### Pitfall 3: No Source Evaluation
**Problem:** Treating all sources equally

**Solution:**
```python
# Evaluate each source
for source in sources:
    credibility = evaluate_credibility(source)
    if credibility['score'] < 5:
        skip_or_flag(source)
```

### Pitfall 4: Missing Citations
**Problem:** Answering without proper attribution

**Solution:**
```
# Always format with citations
answer = f"""
The EU passed the AI Act [1], following the US framework [2].

Sources:
[1] EU AI Act - bbc.com (2026-02-05)
[2] US Framework - reuters.com (2026-02-03)
"""
```

### Pitfall 5: Ignoring Conflicts
**Problem:** Not addressing contradictory information

**Solution:**
```python
if detect_conflicts(sources):
    resolution = resolve_conflicts(sources)
    answer += f"\n\nNote: {resolution['caveat']}"
```

---

## Production Checklist

### Setup Phase
- [ ] Configure LLM API (OpenAI/Anthropic/etc.)
- [ ] Configure Search API (Google/Tavily/Brave)
- [ ] Set knowledge cutoff date
- [ ] Define credibility scoring rules
- [ ] Create error handling strategies

### Query Processing
- [ ] Analyze query for web search need
- [ ] Optimize search queries (2-3 variants)
- [ ] Set maximum results limit
- [ ] Configure timeout handling
- [ ] Implement retry logic

### Result Evaluation
- [ ] Score relevance (0-10)
- [ ] Score freshness (0-10)
- [ ] Score credibility (0-10)
- [ ] Calculate overall score
- [ ] Filter low-quality results (< 6/10)

### Answer Generation
- [ ] Synthesize from multiple sources
- [ ] Add inline citations [1], [2]
- [ ] Include publication dates
- [ ] Add confidence level
- [ ] Note any caveats
- [ ] Format for readability

### Quality Assurance
- [ ] Verify all citations present
- [ ] Check date freshness
- [ ] Confirm source credibility
- [ ] Test conflict handling
- [ ] Validate JSON parsing
- [ ] Monitor API costs

### Monitoring
- [ ] Track search API usage
- [ ] Log query types
- [ ] Monitor response times
- [ ] Track citation accuracy
- [ ] Measure user satisfaction

---

## Quick Reference

### Prompt Component Checklist

```python
prompt = f"""
[✓] Context: Query, Date, Cutoff
[✓] Task: Clear instruction
[✓] Input: Formatted data
[✓] Instructions: Step-by-step
[✓] Output Format: JSON/Markdown
[✓] Evaluation: Scoring criteria
[✓] Edge Cases: Error handling
[✓] Examples: Optional but helpful

Generate [output]:
"""
```

### Response Validation Checklist

```python
def validate_response(response):
    checks = {
        'has_answer': bool(response.get('answer')),
        'has_citations': '[1]' in response.get('answer', ''),
        'has_confidence': 'confidence' in response.lower(),
        'has_sources': bool(response.get('sources')),
        'has_dates': '2026' in response.get('sources', ''),
    }
    return all(checks.values())
```

---

## Summary

**Web Search RAG Prompt Engineering Essentials:**

1. **Query Analysis** - Decide if search needed
2. **Query Optimization** - Create effective search queries
3. **Result Processing** - Structure and score results
4. **Credibility Check** - Evaluate source trustworthiness
5. **Conflict Resolution** - Handle contradictions
6. **Answer Generation** - Synthesize with citations

**Key Principles:**
- Always include context (date, cutoff)
- Request structured output
- Multi-dimensional evaluation
- Mandatory citations
- Confidence indicators
- Handle edge cases

**Success Metrics:**
- Answer accuracy
- Citation completeness
- Source credibility
- Response freshness
- User satisfaction

---

*Generated: 2026-02-06*
*For: Gen AI Course - RAG Module*
*By: RAG Expert Assistant*
