"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Trend Schemas
class TrendBase(BaseModel):
    title: str
    source: Optional[str] = None
    url: Optional[str] = None
    published_at: Optional[datetime] = None


class TrendCreate(TrendBase):
    pass


class Trend(TrendBase):
    id: int
    fetched_at: datetime
    is_processed: bool
    
    class Config:
        from_attributes = True


# Content Schemas
class ContentBase(BaseModel):
    content_type: str
    text: str
    hashtags: Optional[List[str]] = None
    status: str = "draft"
    scheduled_for: Optional[datetime] = None


class ContentCreate(ContentBase):
    trend_id: Optional[int] = None


class Content(ContentBase):
    id: int
    trend_id: Optional[int]
    created_at: datetime
    published_at: Optional[datetime] = None
    telegram_message_id: Optional[int] = None
    
    class Config:
        from_attributes = True


# Performance Metric Schemas
class MetricBase(BaseModel):
    platform: str
    impressions: int = 0
    engagements: int = 0
    clicks: int = 0
    shares: int = 0
    comments: int = 0
    notes: Optional[str] = None


class MetricCreate(MetricBase):
    content_id: int


class PerformanceMetric(MetricBase):
    id: int
    content_id: int
    recorded_at: datetime
    
    class Config:
        from_attributes = True


# Strategy Note Schemas
class StrategyNoteBase(BaseModel):
    insights: str
    recommendations: str


class StrategyNoteCreate(StrategyNoteBase):
    period_start: datetime
    period_end: datetime


class StrategyNote(StrategyNoteBase):
    id: int
    period_start: datetime
    period_end: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


# AI Generation Schemas
class GenerateRequest(BaseModel):
    prompt: str
    context: Optional[str] = None
    model: Optional[str] = None
    json_mode: bool = False


class GenerateResponse(BaseModel):
    content: str
    tokens_used: int
    model: str


# Telegram Callback Schemas
class CallbackAction(BaseModel):
    action: str  # approve, reject, edit, schedule
    content_id: int
    data: Optional[Dict[str, Any]] = None
