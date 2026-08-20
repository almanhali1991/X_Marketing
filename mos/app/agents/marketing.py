"""
Marketing Agent - Core AI agent for content generation
"""
from typing import List, Dict, Optional
from loguru import logger

from ..ai_provider import get_ai_provider
from ..prompts.content import CONTENT_GENERATION_PROMPT, HASHTAG_GENERATION_PROMPT


class MarketingAgent:
    """AI agent for generating marketing content"""
    
    def __init__(self):
        self.provider = get_ai_provider()
    
    async def generate_content(
        self,
        trend_title: str,
        trend_context: str,
        content_type: str = "post",
        language: str = "ar",
    ) -> Dict[str, str]:
        """Generate content based on a trend"""
        
        prompt = CONTENT_GENERATION_PROMPT.format(
            trend_title=trend_title,
            trend_context=trend_context,
            content_type=content_type,
            language=language,
        )
        
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert marketing content creator specializing in "
                    "Saudi/Gulf market trends. Create engaging, original content "
                    "that resonates with Arabic-speaking audiences."
                ),
            },
            {"role": "user", "content": prompt},
        ]
        
        try:
            response = await self.provider.generate(
                messages=messages,
                json_mode=False,
            )
            
            content = self.provider.extract_content(response)
            usage = response.get("usage", {})
            
            logger.info(f"Generated {content_type} content for trend: {trend_title}")
            
            return {
                "content": content,
                "tokens_used": usage.get("total_tokens", 0),
                "model": response.get("model", "unknown"),
            }
            
        except Exception as e:
            logger.error(f"Failed to generate content: {e}")
            raise
    
    async def generate_hashtags(
        self,
        content: str,
        trend_title: str,
        count: int = 5,
    ) -> List[str]:
        """Generate relevant hashtags for content"""
        
        prompt = HASHTAG_GENERATION_PROMPT.format(
            content=content,
            trend_title=trend_title,
            count=count,
        )
        
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a hashtag expert. Generate relevant, trending hashtags "
                    "for Arabic social media content. Return ONLY a JSON array of strings."
                ),
            },
            {"role": "user", "content": prompt},
        ]
        
        try:
            response = await self.provider.generate(
                messages=messages,
                json_mode=True,
            )
            
            content_str = self.provider.extract_content(response)
            
            # Parse hashtags from response (expecting JSON array)
            import json
            try:
                hashtags = json.loads(content_str)
                if isinstance(hashtags, list):
                    return hashtags[:count]
            except json.JSONDecodeError:
                # Fallback: extract hashtags from text
                import re
                hashtags = re.findall(r'#\w+', content_str)
                return hashtags[:count] if hashtags else ["#ترند", "#السعودية"]
            
            return ["#ترند", "#السعودية"]
            
        except Exception as e:
            logger.error(f"Failed to generate hashtags: {e}")
            return ["#ترند", "#السعودية"]
    
    async def analyze_performance(
        self,
        content: str,
        metrics: Dict[str, int],
    ) -> str:
        """Analyze content performance and provide insights"""
        
        prompt = f"""
        Analyze the following content performance:
        
        Content: {content[:500]}...
        
        Metrics:
        - Impressions: {metrics.get('impressions', 0)}
        - Engagements: {metrics.get('engagements', 0)}
        - Clicks: {metrics.get('clicks', 0)}
        - Shares: {metrics.get('shares', 0)}
        - Comments: {metrics.get('comments', 0)}
        
        Provide brief insights and recommendations in Arabic.
        """
        
        messages = [
            {
                "role": "system",
                "content": "You are a marketing analyst. Provide actionable insights in Arabic.",
            },
            {"role": "user", "content": prompt},
        ]
        
        try:
            response = await self.provider.generate(messages=messages)
            return self.provider.extract_content(response)
        except Exception as e:
            logger.error(f"Failed to analyze performance: {e}")
            return "تعذر تحليل الأداء"
