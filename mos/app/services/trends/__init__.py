"""
Trend service - fetches and processes trends from RSS/News sources
"""
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from loguru import logger

from ..repositories import TrendRepository
from ..models import Trend


class TrendService:
    """Service for fetching and processing trends"""
    
    def __init__(self, db: Session):
        self.db = db
        self.trend_repo = TrendRepository(db)
    
    async def fetch_trends_from_sources(self, sources: List[str]) -> int:
        """Fetch trends from RSS/News sources"""
        count = 0
        
        for source_url in sources:
            try:
                feed = feedparser.parse(source_url)
                
                for entry in feed.entries[:10]:  # Limit to 10 per source
                    published = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        published = datetime(*entry.updated_parsed[:6])
                    else:
                        published = datetime.utcnow()
                    
                    # Check if trend already exists (by URL or title)
                    existing = self.db.query(Trend).filter(
                        (Trend.url == entry.get('link')) |
                        (Trend.title == entry.get('title'))
                    ).first()
                    
                    if not existing:
                        self.trend_repo.create(
                            title=entry.get('title', 'No title'),
                            source=feed.feed.get('title', 'Unknown'),
                            url=entry.get('link', ''),
                            published_at=published,
                        )
                        count += 1
                
                logger.info(f"Fetched trends from {source_url}")
                
            except Exception as e:
                logger.error(f"Failed to fetch from {source_url}: {e}")
        
        return count
    
    def get_unprocessed_trends(self) -> List[Trend]:
        """Get all unprocessed trends"""
        return self.trend_repo.get_unprocessed()
    
    def get_recent_trends(self, hours: int = 24) -> List[Trend]:
        """Get trends from the last N hours"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return self.db.query(Trend).filter(
            Trend.fetched_at >= cutoff
        ).order_by(Trend.fetched_at.desc()).all()
