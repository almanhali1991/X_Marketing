"""
Content service - orchestrates content generation workflow
"""
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from loguru import logger

from ..agents.marketing import MarketingAgent
from ..repositories import ContentRepository, TrendRepository
from ..models import Content


class ContentService:
    """Service for content generation and management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.agent = MarketingAgent()
        self.content_repo = ContentRepository(db)
        self.trend_repo = TrendRepository(db)
    
    async def generate_content_for_trend(
        self,
        trend_id: int,
        content_type: str = "post",
        schedule_time: Optional[str] = None,
    ) -> Optional[Content]:
        """Generate content for a specific trend"""
        
        # Get trend from database
        trend = self.db.query(Trend).filter(Trend.id == trend_id).first()
        if not trend:
            logger.error(f"Trend {trend_id} not found")
            return None
        
        try:
            # Generate main content
            result = await self.agent.generate_content(
                trend_title=trend.title,
                trend_context=f"Source: {trend.source}, URL: {trend.url}",
                content_type=content_type,
                language="ar",
            )
            
            # Generate hashtags
            hashtags = await self.agent.generate_hashtags(
                content=result["content"],
                trend_title=trend.title,
                count=5,
            )
            
            # Calculate scheduled time
            scheduled_for = None
            if schedule_time:
                # Parse HH:MM format
                hour, minute = map(int, schedule_time.split(":"))
                scheduled_for = datetime.utcnow().replace(
                    hour=hour, minute=minute, second=0, microsecond=0
                )
                # If time has passed today, schedule for tomorrow
                if scheduled_for < datetime.utcnow():
                    scheduled_for += timedelta(days=1)
            
            # Save to database
            content = self.content_repo.create(
                text=result["content"],
                content_type=content_type,
                trend_id=trend_id,
                hashtags=hashtags,
                scheduled_for=scheduled_for,
            )
            
            # Mark trend as processed
            self.trend_repo.mark_processed(trend_id)
            
            logger.info(f"Generated content ID {content.id} for trend {trend_id}")
            return content
            
        except Exception as e:
            logger.error(f"Failed to generate content for trend {trend_id}: {e}")
            return None
    
    async def review_pending_content(self) -> List[Content]:
        """Get all content pending review"""
        return self.content_repo.get_pending_review()
    
    async def approve_content(self, content_id: int) -> bool:
        """Approve content for scheduling/publication"""
        try:
            self.content_repo.update_status(content_id, "scheduled")
            logger.info(f"Approved content {content_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to approve content {content_id}: {e}")
            return False
    
    async def reject_content(self, content_id: int) -> bool:
        """Reject content"""
        try:
            self.content_repo.update_status(content_id, "rejected")
            logger.info(f"Rejected content {content_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to reject content {content_id}: {e}")
            return False
    
    async def edit_content(self, content_id: int, new_text: str) -> bool:
        """Edit content text"""
        try:
            content = self.db.query(Content).filter(Content.id == content_id).first()
            if content:
                content.text = new_text
                self.db.commit()
                logger.info(f"Edited content {content_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to edit content {content_id}: {e}")
            return False
