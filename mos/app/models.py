"""
Database models for MOS using SQLAlchemy
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Trend(Base):
    """Trending topics from RSS/News sources"""
    __tablename__ = "trends"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    source = Column(String(200))
    url = Column(String(1000))
    published_at = Column(DateTime)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    is_processed = Column(Boolean, default=False)
    
    contents = relationship("Content", back_populates="trend")


class WatchlistItem(Base):
    """Watchlist items from configured sources"""
    __tablename__ = "watchlist_items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    source_url = Column(String(1000))
    content_url = Column(String(1000))
    summary = Column(Text)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    is_processed = Column(Boolean, default=False)


class Content(Base):
    """Generated content drafts"""
    __tablename__ = "contents"
    
    id = Column(Integer, primary_key=True, index=True)
    trend_id = Column(Integer, ForeignKey("trends.id"))
    content_type = Column(String(50))  # post, thread, article
    text = Column(Text, nullable=False)
    hashtags = Column(JSON)
    status = Column(String(50), default="draft")  # draft, scheduled, published, rejected
    scheduled_for = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime)
    telegram_message_id = Column(Integer)
    
    trend = relationship("Trend", back_populates="contents")
    metrics = relationship("PerformanceMetric", back_populates="content")


class PerformanceMetric(Base):
    """Manual performance metrics entered by user"""
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("contents.id"))
    platform = Column(String(50))  # x, linkedin, instagram, etc.
    impressions = Column(Integer, default=0)
    engagements = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    
    content = relationship("Content", back_populates="metrics")


class StrategyNote(Base):
    """Weekly/monthly strategy improvement notes"""
    __tablename__ = "strategy_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    insights = Column(Text)
    recommendations = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class CostLog(Base):
    """AI API cost tracking"""
    __tablename__ = "cost_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100))
    tokens_used = Column(Integer)
    estimated_cost = Column(Float)
    task_type = Column(String(50))  # content, strategy, analysis
    created_at = Column(DateTime, default=datetime.utcnow)
