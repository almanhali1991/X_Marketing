"""
Repository pattern for database operations
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..models import Trend, Content, PerformanceMetric, StrategyNote, CostLog, WatchlistItem


class TrendRepository:
    """Repository for Trend operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, title: str, source: str, url: str, published_at: datetime) -> Trend:
        trend = Trend(
            title=title,
            source=source,
            url=url,
            published_at=published_at,
        )
        self.db.add(trend)
        self.db.commit()
        self.db.refresh(trend)
        return trend
    
    def get_unprocessed(self) -> List[Trend]:
        return self.db.query(Trend).filter(Trend.is_processed == False).all()
    
    def mark_processed(self, trend_id: int):
        self.db.query(Trend).filter(Trend.id == trend_id).update({"is_processed": True})
        self.db.commit()
    
    def get_all(self, limit: int = 100) -> List[Trend]:
        return self.db.query(Trend).order_by(Trend.fetched_at.desc()).limit(limit).all()


class ContentRepository:
    """Repository for Content operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(
        self,
        text: str,
        content_type: str,
        trend_id: Optional[int] = None,
        hashtags: Optional[List[str]] = None,
        scheduled_for: Optional[datetime] = None,
    ) -> Content:
        content = Content(
            text=text,
            content_type=content_type,
            trend_id=trend_id,
            hashtags=hashtags or [],
            scheduled_for=scheduled_for,
        )
        self.db.add(content)
        self.db.commit()
        self.db.refresh(content)
        return content
    
    def get_by_status(self, status: str) -> List[Content]:
        return self.db.query(Content).filter(Content.status == status).all()
    
    def update_status(self, content_id: int, status: str):
        self.db.query(Content).filter(Content.id == content_id).update({"status": status})
        self.db.commit()
    
    def set_telegram_message(self, content_id: int, message_id: int):
        self.db.query(Content).filter(Content.id == content_id).update({
            "telegram_message_id": message_id
        })
        self.db.commit()
    
    def get_pending_review(self) -> List[Content]:
        return self.db.query(Content).filter(Content.status == "draft").all()
    
    def get_scheduled(self) -> List[Content]:
        now = datetime.utcnow()
        return self.db.query(Content).filter(
            Content.status == "scheduled",
            Content.scheduled_for <= now,
        ).all()


class MetricRepository:
    """Repository for PerformanceMetric operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(
        self,
        content_id: int,
        platform: str,
        impressions: int = 0,
        engagements: int = 0,
        **kwargs
    ) -> PerformanceMetric:
        metric = PerformanceMetric(
            content_id=content_id,
            platform=platform,
            impressions=impressions,
            engagements=engagements,
            clicks=kwargs.get("clicks", 0),
            shares=kwargs.get("shares", 0),
            comments=kwargs.get("comments", 0),
            notes=kwargs.get("notes"),
        )
        self.db.add(metric)
        self.db.commit()
        self.db.refresh(metric)
        return metric
    
    def get_by_content(self, content_id: int) -> List[PerformanceMetric]:
        return self.db.query(PerformanceMetric).filter(
            PerformanceMetric.content_id == content_id
        ).all()


class WatchlistRepository:
    """Repository for WatchlistItem operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(
        self,
        title: str,
        source_url: str,
        content_url: str,
        summary: Optional[str] = None,
    ) -> WatchlistItem:
        item = WatchlistItem(
            title=title,
            source_url=source_url,
            content_url=content_url,
            summary=summary,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def get_unprocessed(self) -> List[WatchlistItem]:
        return self.db.query(WatchlistItem).filter(
            WatchlistItem.is_processed == False
        ).all()
    
    def mark_processed(self, item_id: int):
        self.db.query(WatchlistItem).filter(WatchlistItem.id == item_id).update({
            "is_processed": True
        })
        self.db.commit()


class CostLogRepository:
    """Repository for CostLog operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_cost(
        self,
        model_name: str,
        tokens_used: int,
        estimated_cost: float,
        task_type: str,
    ) -> CostLog:
        log = CostLog(
            model_name=model_name,
            tokens_used=tokens_used,
            estimated_cost=estimated_cost,
            task_type=task_type,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
