"""
ADVANCED WEB SEARCH RAG PROMPT PATTERNS
========================================

This file contains specialized prompt patterns for different Web Search RAG scenarios.
"""

# ========================================
# PATTERN 1: TIME-SENSITIVE QUERIES
# ========================================

TIME_SENSITIVE_PROMPT = """
You are answering a time-sensitive query using web search results.

User Query: {query}
Current Time: {current_datetime}
Query Type: {query_type}  # breaking_news / live_data / recent_event

Web Results (sorted by recency):
{results}

Special Instructions for Time-Sensitive Content:
1. Lead with the MOST RECENT information
2. Include timestamps prominently (e.g., "As of 2:30 PM EST...")
3. Flag if information is "breaking" or "developing"
4. Warn if sources are more than 24 hours old for breaking news
5. Note if different sources have different update times

Format:
**Latest Information (as of {most_recent_source_time}):**
[Answer with explicit time references]

**Sources (newest first):**
[1] Title - Source - Published: [timestamp]
[2] Title - Source - Published: [timestamp]

⚠️ **Update Frequency:** This information may change rapidly. Last checked: {current_time}

Generate time-aware answer:
"""

# Example Usage
TIME_SENSITIVE_EXAMPLE = """
User Query: "What's the current Bitcoin price?"
Current Time: 2026-02-06 14:30:00 EST

Web Results:
[1] Bitcoin trades at $52,340 - CoinDesk - 2026-02-06 14:25:00
[2] BTC hits $52,000 - Reuters - 2026-02-06 14:15:00
[3] Bitcoin surges past $51,500 - Bloomberg - 2026-02-06 13:45:00

Output:
**Latest Information (as of 2:25 PM EST):**
Bitcoin is currently trading at $52,340 [1], showing a continued upward trend. 
The price crossed $52,000 just 15 minutes ago according to Reuters [2], and has 
been climbing since 1:45 PM when it surpassed $51,500 [3].

**Sources (newest first):**
[1] Bitcoin Price Update - CoinDesk - Published: Feb 6, 2026, 2:25 PM EST
[2] BTC Breaks $52K - Reuters - Published: Feb 6, 2026, 2:15 PM EST

⚠️ **Update Frequency:** Cryptocurrency prices change every second. 
Last checked: Feb 6, 2026, 2:30 PM EST
"""


# ========================================
# PATTERN 2: MULTI-PERSPECTIVE SYNTHESIS
# ========================================

MULTI_PERSPECTIVE_PROMPT = """
You are synthesizing information from multiple sources with different perspectives.

User Query: {query}
Topic: {topic}
Current Date: {current_date}

Sources by Perspective:
[Official/Government Sources]:
{official_sources}

[News Media Sources]:
{news_sources}

[Industry/Expert Sources]:
{expert_sources}

[Social Media/Public Sentiment]:
{social_sources}

Task:
1. Identify the main narrative from each perspective
2. Note where perspectives agree vs. diverge
3. Highlight any biases or conflicts of interest
4. Synthesize a balanced view
5. Let the user know if consensus exists or if topic is controversial

Format:
**Consensus Points:**
- [Points where most sources agree]

**Divergent Perspectives:**
- Official view: [summary with citations]
- Media coverage: [summary with citations]
- Expert opinion: [summary with citations]
- Public sentiment: [summary with citations]

**Analysis:**
[Your balanced synthesis noting any notable patterns or concerns]

**Recommendation:**
[Given the disagreement/consensus, what should the user know?]

Generate multi-perspective analysis:
"""

# Example
MULTI_PERSPECTIVE_EXAMPLE = """
Query: "Is the new AI regulation bill good for innovation?"

Consensus Points:
- All sources agree the bill will create new compliance requirements [1,2,3,4]
- Most acknowledge increased transparency obligations [1,2,5]

Divergent Perspectives:
- Official view: Government sources [1] emphasize consumer protection benefits
- Media coverage: News outlets [2,3] focus on potential economic impacts
- Expert opinion: Tech industry leaders [4] warn of competitiveness concerns
- Academic perspective: Researchers [5] note need for nuanced implementation

Analysis:
The sources reveal a classic tension between regulation and innovation.
Government emphasizes safety, industry warns of constraints, and academics
suggest the outcome depends heavily on implementation details.

Recommendation:
This is a developing policy debate without clear consensus. The impact will
likely depend on final bill language and enforcement mechanisms. Monitor
updates from multiple source types for balanced perspective.
"""


# ========================================
# PATTERN 3: FACT-CHECKING WITH WEB SEARCH
# ========================================

FACT_CHECK_PROMPT = """
You are fact-checking a claim using web search results.

Claim to Verify: {claim}
Claimed Source: {claimed_source}
Claim Date: {claim_date}
Current Date: {current_date}

Web Search Findings:
{search_results}

Fact-Check Framework:
1. VERIFY: Can you find the original source?
2. CORROBORATE: Do multiple independent sources confirm?
3. CONTEXT: Is the claim missing important context?
4. CREDIBILITY: Are sources authoritative?
5. RECENCY: Is information current or outdated?

Verdict Options:
- TRUE: Confirmed by multiple credible sources
- MOSTLY TRUE: Accurate but missing context
- MIXED: Partially true, partially false
- MOSTLY FALSE: Misleading or missing key context
- FALSE: Contradicted by credible sources
- UNVERIFIABLE: Insufficient evidence

Format:
**Verdict:** [TRUE/MOSTLY TRUE/MIXED/MOSTLY FALSE/FALSE/UNVERIFIABLE]

**Evidence:**
Supporting: [Citations]
Contradicting: [Citations]
Missing Context: [What's not being mentioned]

**Credibility Assessment:**
- Source quality: [High/Medium/Low]
- Number of independent confirmations: [X]
- Most authoritative source: [Which one and why]

**Conclusion:**
[1-2 sentence summary of fact-check]

**Full Explanation:**
[Detailed reasoning with citations]

Perform fact-check:
"""


# ========================================
# PATTERN 4: BREAKING NEWS AGGREGATION
# ========================================

BREAKING_NEWS_PROMPT = """
You are aggregating breaking news from multiple real-time sources.

Breaking News Topic: {topic}
Alert Time: {alert_time}
Last Update: {last_update}

Live Sources (by update time):
{live_sources}

Instructions:
1. Create a chronological timeline of developments
2. Flag conflicting reports with ⚠️
3. Mark unconfirmed information with 🔄
4. Highlight official statements with ✓
5. Note when information is "developing" or "unconfirmed"

Timeline Format:
**{time}** - {headline} [{source}]
   Details: {brief_description}
   Status: ✓ Confirmed / 🔄 Developing / ⚠️ Unconfirmed

**What We Know:**
- [Confirmed facts]

**What's Unclear:**
- [Conflicting reports or gaps]

**What to Watch:**
- [Expected updates or developing angles]

⏱️ **This is a developing story. Last updated: {last_update}**

Generate breaking news summary:
"""


# ========================================
# PATTERN 5: PRODUCT/SERVICE COMPARISON
# ========================================

COMPARISON_SEARCH_PROMPT = """
You are comparing products/services using current web information.

Comparison Request: {comparison_query}
Items to Compare: {items}
Current Date: {current_date}

Web Results:
{results}

Comparison Criteria:
1. Features/Specifications
2. Pricing (current as of {current_date})
3. User Reviews/Ratings
4. Expert Opinions
5. Recent Updates/Changes
6. Availability

Format as Comparison Table:

| Criteria | {item_1} | {item_2} | {item_3} |
|----------|----------|----------|----------|
| Price | ${price} [source] | ${price} [source] | ${price} [source] |
| Rating | X/5 ⭐ ({n} reviews) | Y/5 ⭐ ({n} reviews) | Z/5 ⭐ ({n} reviews) |
| Key Feature | [feature] | [feature] | [feature] |
| Updated | [date] | [date] | [date] |

**Strengths by Product:**
- {item_1}: [key advantages]
- {item_2}: [key advantages]
- {item_3}: [key advantages]

**Best For:**
- {item_1}: [use case]
- {item_2}: [use case]
- {item_3}: [use case]

⚠️ **Price Accuracy:** Prices verified as of {current_date}. May vary by region/retailer.

Generate comparison:
"""


# ========================================
# PATTERN 6: LOCATION-BASED WEB SEARCH
# ========================================

LOCATION_BASED_PROMPT = """
You are answering a location-specific query using web search.

User Query: {query}
Location: {user_location}
Query Type: {type}  # weather/local_news/events/services

Web Results:
{results}

Location-Specific Instructions:
1. Prioritize results from or about the specified location
2. Include local time zone information
3. Mention regional variations if relevant
4. Flag if search results are from different location
5. Include local context (e.g., "In {city}, ...")

Format:
**For {location}:**
[Location-specific answer]

**Local Details:**
- Time Zone: {timezone}
- Current Local Time: {local_time}
- Additional Context: [any relevant local information]

**Sources:**
[Local sources prioritized]

⚠️ Information is specific to {location}. Results may differ for other areas.

Generate location-aware answer:
"""


# ========================================
# PATTERN 7: RESEARCH SYNTHESIS
# ========================================

RESEARCH_SYNTHESIS_PROMPT = """
You are synthesizing research findings from academic and expert sources.

Research Question: {research_question}
Date Range: {date_range}
Current Date: {current_date}

Search Results:
[Academic Papers]:
{academic_sources}

[Industry Reports]:
{industry_sources}

[Expert Commentary]:
{expert_sources}

[News Coverage]:
{news_sources}

Synthesis Instructions:
1. Summarize key findings across sources
2. Note methodology differences
3. Identify consensus vs. debate
4. Highlight most recent/rigorous studies
5. Note limitations and gaps

Format:
**Research Consensus:**
[What most studies agree on - with citations]

**Key Findings:**
1. [Finding 1] - [Studies supporting it]
2. [Finding 2] - [Studies supporting it]
3. [Finding 3] - [Studies supporting it]

**Ongoing Debates:**
- [Contested point]: 
  • Pro: [sources and arguments]
  • Con: [sources and arguments]

**Methodological Notes:**
[Any important methodology considerations]

**Research Gaps:**
[What's not yet well-studied]

**Most Authoritative Sources:**
[Which sources are most reliable and why]

Generate research synthesis:
"""


# ========================================
# PATTERN 8: SENTIMENT-AWARE SEARCH
# ========================================

SENTIMENT_AWARE_PROMPT = """
You are analyzing web results for both facts AND sentiment.

Topic: {topic}
Current Date: {current_date}

Web Results:
{results}

Dual Analysis Required:
1. FACTUAL: What are the objective facts?
2. SENTIMENT: What is the general tone/reaction?

Sentiment Categories:
- Positive/Optimistic
- Negative/Concerned
- Neutral/Mixed
- Skeptical/Questioning

Format:
**Factual Summary:**
[Objective facts from sources - cited]

**Sentiment Analysis:**
Overall Sentiment: [Positive/Negative/Neutral/Mixed]

Breakdown:
- Positive mentions: X% [examples]
- Negative mentions: Y% [examples]
- Neutral coverage: Z% [examples]

**Notable Quotes:**
- Positive: "[quote]" - [source]
- Critical: "[quote]" - [source]

**Sentiment Shift:**
[Is sentiment changing over time? Note any trends]

**Balanced Perspective:**
[Your synthesis considering both facts and sentiment]

Generate sentiment-aware analysis:
"""


# ========================================
# USAGE GUIDE
# ========================================

USAGE_GUIDE = """
HOW TO USE THESE PROMPTS
========================

1. TIME-SENSITIVE: Use for stock prices, weather, live sports, breaking news
2. MULTI-PERSPECTIVE: Use for controversial topics, policy debates, complex issues
3. FACT-CHECKING: Use when verifying claims or debunking misinformation
4. BREAKING NEWS: Use for developing stories, emergencies, live events
5. COMPARISON: Use for product research, service comparisons, alternatives
6. LOCATION-BASED: Use for local queries, weather, events, services
7. RESEARCH SYNTHESIS: Use for academic topics, scientific questions
8. SENTIMENT-AWARE: Use for brand monitoring, public opinion, reaction tracking

BEST PRACTICES:
- Always include current date/time
- Request explicit citations
- Ask for confidence levels
- Specify output format
- Include verification steps
- Note when information is developing
- Flag conflicts or uncertainties
"""

print(USAGE_GUIDE)
