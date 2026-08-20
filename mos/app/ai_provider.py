"""
NVIDIA NIM AI Provider - OpenAI-compatible API client
"""
import httpx
from typing import Optional, Dict, Any, List
from loguru import logger

from .config import get_settings


class NVIDIAProvider:
    """AI provider for NVIDIA NIM API (OpenAI-compatible)"""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.NIM_BASE_URL
        self.api_key = self.settings.NIM_API_KEY
        self.default_model = self.settings.NIM_MODEL
        self.strategy_model = self.settings.NIM_STRATEGY_MODEL
        self.max_tokens = self.settings.NIM_MAX_TOKENS
        self.temperature = self.settings.NIM_TEMPERATURE
    
    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        json_mode: bool = False,
    ) -> Dict[str, Any]:
        """Generate text using NVIDIA NIM API"""
        
        model = model or self.default_model
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature or self.temperature
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
        }
        
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
                
                # Log usage for cost tracking
                usage = result.get("usage", {})
                if usage:
                    logger.info(
                        f"NIM API usage: {usage.get('total_tokens', 0)} tokens "
                        f"(prompt: {usage.get('prompt_tokens', 0)}, "
                        f"completion: {usage.get('completion_tokens', 0)})"
                    )
                
                return result
                
        except httpx.HTTPError as e:
            logger.error(f"NIM API HTTP error: {e}")
            raise
        except Exception as e:
            logger.error(f"NIM API error: {e}")
            raise
    
    def extract_content(self, response: Dict[str, Any]) -> str:
        """Extract text content from API response"""
        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to extract content from response: {e}")
            return ""
    
    def estimate_cost(self, tokens_used: int, model: Optional[str] = None) -> float:
        """Estimate cost based on token usage (approximate rates)"""
        # Free tier models have $0 cost, but we track for quota management
        # These are placeholder rates - actual free tier has monthly credits
        model = model or self.default_model
        
        # Most NIM models are free within monthly credit limits
        # Return 0.0 for free tier tracking
        return 0.0


# Global provider instance
_provider: Optional[NVIDIAProvider] = None


def get_ai_provider() -> NVIDIAProvider:
    """Get or create AI provider instance"""
    global _provider
    if _provider is None:
        _provider = NVIDIAProvider()
    return _provider
