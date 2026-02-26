"""Pydantic models for aumai-bharatvaani."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

__all__ = [
    "IndicLanguage",
    "SentimentResult",
    "NEREntity",
]


class IndicLanguage(BaseModel):
    """Metadata for one of the 22 Indian scheduled languages."""

    code: str = Field(description="BCP-47 code, e.g. 'hi'.")
    name: str = Field(description="English name.")
    name_native: str = Field(description="Name in the native script.")
    script: str
    speakers_millions: float = Field(ge=0.0)


class SentimentResult(BaseModel):
    """Sentiment analysis result for Indic text."""

    text: str
    language: str
    sentiment: Literal["positive", "negative", "neutral"]
    score: float = Field(ge=-1.0, le=1.0, description="Positive values = positive sentiment.")


class NEREntity(BaseModel):
    """A named entity extracted from Indic text."""

    text: str
    entity_type: str = Field(description="PERSON, LOCATION, ORGANIZATION, etc.")
    start: int = Field(ge=0)
    end: int = Field(ge=0)
    language: str
