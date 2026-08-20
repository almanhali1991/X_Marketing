"""
Scheduler service - handles scheduled content notifications
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from loguru import logger

from ..config import get_settings
from ..database import SessionLocal
from ..models import Content
from ..services.content import ContentService


class SchedulerService:
    """Service for scheduling content and automated tasks"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.settings = get_settings()
    
    async def check_scheduled_content(self):
        """Check for content that should be notified to user"""
        db = SessionLocal()
        try:
            now = datetime.utcnow()
            # Get content scheduled for now or earlier
            scheduled_contents = db.query(Content).filter(
                Content.status == "scheduled",
                Content.scheduled_for <= now,
            ).all()
            
            for content in scheduled_contents:
                logger.info(f"Scheduled content {content.id} ready for notification")
                # In full implementation, this would send Telegram notification
                # For MVP, content is already in DB ready for review
            
        except Exception as e:
            logger.error(f"Error checking scheduled content: {e}")
        finally:
            db.close()
    
    async def fetch_trends_periodically(self):
        """Periodically fetch trends from sources"""
        from ..services.trends import TrendService
        
        db = SessionLocal()
        try:
            trend_service = TrendService(db)
            count = await trend_service.fetch_trends_from_sources(
                self.settings.TREND_SOURCES
            )
            logger.info(f"Fetched {count} new trends")
        except Exception as e:
            logger.error(f"Error fetching trends: {e}")
        finally:
            db.close()
    
    def start(self):
        """Start the scheduler with configured jobs"""
        if not self.settings.SCHEDULER_ENABLED:
            logger.info("Scheduler disabled")
            return
        
        # Add job to check scheduled content every hour
        self.scheduler.add_job(
            self.check_scheduled_content,
            trigger=CronTrigger(minute=0),  # Every hour at minute 0
            id="check_scheduled_content",
            name="Check scheduled content",
            replace_existing=True,
        )
        
        # Add job to fetch trends every 6 hours
        self.scheduler.add_job(
            self.fetch_trends_periodically,
            trigger=CronTrigger(hour="*/6"),  # Every 6 hours
            id="fetch_trends",
            name="Fetch trends from sources",
            replace_existing=True,
        )
        
        self.scheduler.start()
        logger.info("Scheduler started with jobs")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler shutdown complete")


def run_scheduler():
    """Run the scheduler (blocking)"""
    import asyncio
    
    scheduler = SchedulerService()
    scheduler.start()
    
    logger.info("Scheduler running... Press Ctrl+C to stop.")
    
    try:
        # Keep running
        while True:
            asyncio.run(asyncio.sleep(1))
    except KeyboardInterrupt:
        logger.info("Stopping scheduler...")
        scheduler.shutdown()
