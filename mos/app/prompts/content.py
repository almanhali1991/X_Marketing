"""
AI prompts for content generation
"""

CONTENT_GENERATION_PROMPT = """
Based on the following trend, create engaging {content_type} content in {language}.

Trend: {trend_title}
Context: {trend_context}

Requirements:
1. Content must be original and creative
2. Tailored for Saudi/Gulf audience
3. Engaging tone appropriate for social media
4. Length suitable for a {content_type}
5. Include relevant emojis if appropriate
6. Do NOT include hashtags (they will be generated separately)

Generate the content now:
"""

HASHTAG_GENERATION_PROMPT = """
Generate exactly {count} relevant hashtags for the following content.

Content: {content}
Trend: {trend_title}

Return ONLY a JSON array of strings, like: ["#hashtag1", "#hashtag2"]
"""

TREND_ANALYSIS_PROMPT = """
Analyze the following trends and identify the most relevant ones for our marketing strategy.

Trends:
{trends_list}

Consider:
1. Relevance to Saudi/Gulf market
2. Potential for engagement
3. Brand alignment
4. Timeliness

Return a JSON object with:
- selected_trends: list of trend titles
- reasoning: brief explanation in Arabic
"""

STRATEGY_IMPROVEMENT_PROMPT = """
Based on the following performance data, provide strategy recommendations.

Recent Content Performance:
{performance_summary}

Provide:
1. Key insights (in Arabic)
2. Recommended actions (in Arabic)
3. Content types to focus on
4. Optimal posting times

Return as structured JSON with fields: insights, actions, content_types, posting_times
"""

WATCHLIST_MONITOR_PROMPT = """
Summarize the following watchlist item for marketing intelligence.

Title: {title}
Source: {source}
Content: {content}

Provide a brief summary (2-3 sentences in Arabic) highlighting:
- Key information
- Marketing relevance
- Potential action items
"""
