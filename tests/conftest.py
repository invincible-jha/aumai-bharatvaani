"""Shared test fixtures for aumai-bharatvaani."""

from __future__ import annotations

import pytest

from aumai_bharatvaani.core import (
    IndicNER,
    IndicSentimentAnalyzer,
    IndicTokenizer,
    IndicTransliterator,
)


@pytest.fixture()
def tokenizer() -> IndicTokenizer:
    """A fresh IndicTokenizer instance."""
    return IndicTokenizer()


@pytest.fixture()
def sentiment_analyzer() -> IndicSentimentAnalyzer:
    """A fresh IndicSentimentAnalyzer instance."""
    return IndicSentimentAnalyzer()


@pytest.fixture()
def ner() -> IndicNER:
    """A fresh IndicNER instance."""
    return IndicNER()


@pytest.fixture()
def transliterator() -> IndicTransliterator:
    """A fresh IndicTransliterator instance."""
    return IndicTransliterator()
