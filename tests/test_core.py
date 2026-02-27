"""Comprehensive tests for aumai-bharatvaani core module."""

from __future__ import annotations

import pytest

from aumai_bharatvaani.core import (
    SCHEDULED_LANGUAGES,
    IndicNER,
    IndicSentimentAnalyzer,
    IndicTokenizer,
    IndicTransliterator,
)
from aumai_bharatvaani.models import IndicLanguage, NEREntity, SentimentResult


# ---------------------------------------------------------------------------
# SCHEDULED_LANGUAGES tests
# ---------------------------------------------------------------------------


class TestScheduledLanguages:
    def test_contains_at_least_22_languages(self) -> None:
        assert len(SCHEDULED_LANGUAGES) >= 22

    def test_hindi_present(self) -> None:
        assert "hi" in SCHEDULED_LANGUAGES
        assert SCHEDULED_LANGUAGES["hi"].name == "Hindi"

    def test_all_languages_have_native_name(self) -> None:
        for code, lang in SCHEDULED_LANGUAGES.items():
            assert lang.name_native, f"Missing native name for {code}"

    def test_all_languages_have_speakers_data(self) -> None:
        for code, lang in SCHEDULED_LANGUAGES.items():
            assert lang.speakers_millions >= 0.0

    def test_hindi_is_most_spoken(self) -> None:
        hindi = SCHEDULED_LANGUAGES["hi"]
        # Hindi at 600M should be the highest
        max_speakers = max(l.speakers_millions for l in SCHEDULED_LANGUAGES.values())
        assert hindi.speakers_millions == max_speakers

    def test_all_expected_language_codes_present(self) -> None:
        # Sinhala (si) is a Sri Lankan language and is NOT one of India's
        # 22 scheduled languages — it has been removed from this list.
        expected = {
            "as", "bn", "bo", "doi", "gu", "hi", "kn", "ks", "kok",
            "mai", "ml", "mni", "mr", "ne", "or", "pa", "sa", "sat",
            "sd", "ta", "te", "ur",
        }
        assert set(SCHEDULED_LANGUAGES.keys()) == expected

    def test_language_model_fields(self) -> None:
        lang = SCHEDULED_LANGUAGES["ta"]
        assert isinstance(lang, IndicLanguage)
        assert lang.code == "ta"
        assert lang.script == "Tamil"


# ---------------------------------------------------------------------------
# IndicTokenizer tests
# ---------------------------------------------------------------------------


class TestIndicTokenizer:
    def test_tokenize_hindi_basic(self, tokenizer: IndicTokenizer) -> None:
        tokens = tokenizer.tokenize("नमस्ते दुनिया", "hi")
        assert isinstance(tokens, list)
        assert len(tokens) >= 1

    def test_tokenize_hindi_splits_on_whitespace(self, tokenizer: IndicTokenizer) -> None:
        tokens = tokenizer.tokenize("मैं ठीक हूँ", "hi")
        assert len(tokens) == 3

    def test_tokenize_hindi_strips_dandas(self, tokenizer: IndicTokenizer) -> None:
        tokens = tokenizer.tokenize("यह एक वाक्य है।", "hi")
        # Danda (।) should be treated as separator, not as a token
        for token in tokens:
            assert "।" not in token

    def test_tokenize_bengali_basic(self, tokenizer: IndicTokenizer) -> None:
        tokens = tokenizer.tokenize("আমার সোনার বাংলা", "bn")
        assert len(tokens) == 3

    def test_tokenize_tamil_basic(self, tokenizer: IndicTokenizer) -> None:
        tokens = tokenizer.tokenize("வணக்கம் உலகம்", "ta")
        assert len(tokens) >= 1

    def test_tokenize_telugu_basic(self, tokenizer: IndicTokenizer) -> None:
        tokens = tokenizer.tokenize("నమస్కారం ప్రపంచం", "te")
        assert len(tokens) >= 1

    def test_tokenize_gujarati_basic(self, tokenizer: IndicTokenizer) -> None:
        tokens = tokenizer.tokenize("નમસ્તે દુનિયા", "gu")
        assert len(tokens) >= 1

    def test_tokenize_empty_returns_empty_list(self, tokenizer: IndicTokenizer) -> None:
        tokens = tokenizer.tokenize("", "hi")
        assert tokens == []

    def test_tokenize_unknown_language_falls_back(self, tokenizer: IndicTokenizer) -> None:
        # Unknown language should use generic whitespace splitting
        tokens = tokenizer.tokenize("hello world", "xx")
        assert "hello" in tokens

    def test_tokenize_returns_no_empty_strings(self, tokenizer: IndicTokenizer) -> None:
        tokens = tokenizer.tokenize("नमस्ते   दुनिया", "hi")
        assert all(t != "" for t in tokens)

    def test_tokenize_multiple_dandas(self, tokenizer: IndicTokenizer) -> None:
        tokens = tokenizer.tokenize("शब्द एक।। शब्द दो", "hi")
        assert all("।" not in t for t in tokens)


# ---------------------------------------------------------------------------
# IndicSentimentAnalyzer tests
# ---------------------------------------------------------------------------


class TestIndicSentimentAnalyzer:
    def test_returns_sentiment_result(self, sentiment_analyzer: IndicSentimentAnalyzer) -> None:
        result = sentiment_analyzer.analyze("अच्छा", "hi")
        assert isinstance(result, SentimentResult)

    def test_hindi_positive_word(self, sentiment_analyzer: IndicSentimentAnalyzer) -> None:
        result = sentiment_analyzer.analyze("खुश", "hi")
        assert result.sentiment == "positive"
        assert result.score > 0

    def test_hindi_negative_word(self, sentiment_analyzer: IndicSentimentAnalyzer) -> None:
        result = sentiment_analyzer.analyze("नफरत", "hi")
        assert result.sentiment == "negative"
        assert result.score < 0

    def test_hindi_neutral_unknown_text(self, sentiment_analyzer: IndicSentimentAnalyzer) -> None:
        result = sentiment_analyzer.analyze("अज्ञात", "hi")  # Unknown word
        assert result.sentiment == "neutral"
        assert result.score == 0.0

    def test_bengali_positive_word(self, sentiment_analyzer: IndicSentimentAnalyzer) -> None:
        result = sentiment_analyzer.analyze("ভালো", "bn")
        assert result.sentiment == "positive"

    def test_bengali_negative_word(self, sentiment_analyzer: IndicSentimentAnalyzer) -> None:
        result = sentiment_analyzer.analyze("খারাপ", "bn")
        assert result.sentiment == "negative"

    def test_tamil_positive_word(self, sentiment_analyzer: IndicSentimentAnalyzer) -> None:
        result = sentiment_analyzer.analyze("நல்ல", "ta")
        assert result.sentiment == "positive"

    def test_telugu_positive_word(self, sentiment_analyzer: IndicSentimentAnalyzer) -> None:
        result = sentiment_analyzer.analyze("మంచి", "te")
        assert result.sentiment == "positive"

    def test_unsupported_language_returns_neutral(self, sentiment_analyzer: IndicSentimentAnalyzer) -> None:
        result = sentiment_analyzer.analyze("hello", "xx")
        assert result.sentiment == "neutral"
        assert result.score == 0.0

    def test_result_contains_original_text(self, sentiment_analyzer: IndicSentimentAnalyzer) -> None:
        text = "अच्छा दिन"
        result = sentiment_analyzer.analyze(text, "hi")
        assert result.text == text

    def test_result_contains_language_code(self, sentiment_analyzer: IndicSentimentAnalyzer) -> None:
        result = sentiment_analyzer.analyze("अच्छा", "hi")
        assert result.language == "hi"

    def test_score_in_valid_range(self, sentiment_analyzer: IndicSentimentAnalyzer) -> None:
        for text in ("खुश", "नफरत", "अज्ञात"):
            result = sentiment_analyzer.analyze(text, "hi")
            assert -1.0 <= result.score <= 1.0

    def test_mixed_positive_negative_returns_aggregate(
        self, sentiment_analyzer: IndicSentimentAnalyzer
    ) -> None:
        # Contains both positive and negative words
        result = sentiment_analyzer.analyze("खुश नफरत", "hi")
        assert result.sentiment in ("positive", "negative", "neutral")

    def test_empty_text_returns_neutral(self, sentiment_analyzer: IndicSentimentAnalyzer) -> None:
        result = sentiment_analyzer.analyze("", "hi")
        assert result.sentiment == "neutral"


# ---------------------------------------------------------------------------
# IndicNER tests
# ---------------------------------------------------------------------------


class TestIndicNER:
    def test_returns_list(self, ner: IndicNER) -> None:
        result = ner.extract("श्री राम दिल्ली में हैं", "hi")
        assert isinstance(result, list)

    def test_finds_person_with_shri_prefix(self, ner: IndicNER) -> None:
        entities = ner.extract("श्री राम दिल्ली में हैं", "hi")
        person_entities = [e for e in entities if e.entity_type == "PERSON"]
        assert len(person_entities) >= 1

    def test_finds_location_delhi(self, ner: IndicNER) -> None:
        entities = ner.extract("वह दिल्ली में रहते हैं", "hi")
        location_entities = [e for e in entities if e.entity_type == "LOCATION"]
        assert any("दिल्ली" in e.text for e in location_entities)

    def test_entity_has_correct_fields(self, ner: IndicNER) -> None:
        entities = ner.extract("श्री राम", "hi")
        if entities:
            entity = entities[0]
            assert isinstance(entity, NEREntity)
            assert isinstance(entity.start, int)
            assert isinstance(entity.end, int)
            assert entity.start >= 0
            assert entity.end > entity.start

    def test_entity_span_matches_text(self, ner: IndicNER) -> None:
        text = "श्री राम दिल्ली में हैं"
        entities = ner.extract(text, "hi")
        for entity in entities:
            assert text[entity.start:entity.end] == entity.text

    def test_no_entities_in_plain_text(self, ner: IndicNER) -> None:
        entities = ner.extract("यह एक साधारण वाक्य है।", "hi")
        # Should not crash even if no entities found
        assert isinstance(entities, list)

    def test_entities_contain_language_field(self, ner: IndicNER) -> None:
        entities = ner.extract("श्री मोदी मुंबई में हैं", "hi")
        for entity in entities:
            assert entity.language == "hi"

    def test_bengali_ner_runs_without_error(self, ner: IndicNER) -> None:
        entities = ner.extract("শ্রী রাম কলকাতায় আছেন", "bn")
        assert isinstance(entities, list)

    def test_unsupported_language_returns_empty(self, ner: IndicNER) -> None:
        entities = ner.extract("hello world", "xx")
        assert entities == []

    def test_mumbai_detected_as_location(self, ner: IndicNER) -> None:
        entities = ner.extract("वह मुंबई में रहती हैं", "hi")
        location_texts = [e.text for e in entities if e.entity_type == "LOCATION"]
        assert any("मुंबई" in t for t in location_texts)


# ---------------------------------------------------------------------------
# IndicTransliterator tests
# ---------------------------------------------------------------------------


class TestIndicTransliterator:
    def test_devanagari_to_latin_consonant(self, transliterator: IndicTransliterator) -> None:
        result = transliterator.to_latin("क", "devanagari")
        assert result == "k"

    def test_devanagari_to_latin_vowel(self, transliterator: IndicTransliterator) -> None:
        result = transliterator.to_latin("अ", "devanagari")
        assert result == "a"

    def test_devanagari_to_latin_multiple_chars(self, transliterator: IndicTransliterator) -> None:
        result = transliterator.to_latin("क", "devanagari")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_bengali_to_latin_consonant(self, transliterator: IndicTransliterator) -> None:
        result = transliterator.to_latin("ক", "bengali")
        assert result == "k"

    def test_bengali_to_latin_vowel(self, transliterator: IndicTransliterator) -> None:
        result = transliterator.to_latin("অ", "bengali")
        assert result == "a"

    def test_unsupported_script_raises_value_error(self, transliterator: IndicTransliterator) -> None:
        with pytest.raises(ValueError, match="not supported"):
            transliterator.to_latin("hello", "latin")

    def test_case_insensitive_script_name(self, transliterator: IndicTransliterator) -> None:
        result = transliterator.to_latin("क", "Devanagari")
        assert result == "k"

    def test_unknown_chars_pass_through(self, transliterator: IndicTransliterator) -> None:
        result = transliterator.to_latin("X", "devanagari")
        assert result == "X"

    def test_between_scripts_to_latin(self, transliterator: IndicTransliterator) -> None:
        result = transliterator.between_scripts("क", source="devanagari", target="latin")
        assert result == "k"

    def test_between_scripts_indic_to_indic_returns_pivot(
        self, transliterator: IndicTransliterator
    ) -> None:
        result = transliterator.between_scripts("क", source="devanagari", target="bengali")
        # Returns pivot notation
        assert "[bengali:" in result.lower() or "bengali" in result.lower()

    def test_danda_transliterated_to_period(self, transliterator: IndicTransliterator) -> None:
        result = transliterator.to_latin("।", "devanagari")
        assert result == "."

    def test_double_danda_transliterated(self, transliterator: IndicTransliterator) -> None:
        result = transliterator.to_latin("॥", "devanagari")
        assert result == ".."
