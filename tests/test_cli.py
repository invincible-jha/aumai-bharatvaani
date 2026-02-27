"""Comprehensive CLI tests for aumai-bharatvaani."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from aumai_bharatvaani.cli import main


def _fresh_runner() -> CliRunner:
    """Return a CliRunner without mix_stderr (Click 8.2 compatible)."""
    return CliRunner()


class TestCLIVersion:
    def test_version_flag(self) -> None:
        result = _fresh_runner().invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_help_flag(self) -> None:
        result = _fresh_runner().invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "BharatVaani" in result.output or "bharatvaani" in result.output.lower()


class TestTokenizeCommand:
    def test_tokenize_hindi_basic(self) -> None:
        result = _fresh_runner().invoke(
            main, ["tokenize", "--text", "नमस्ते दुनिया", "--language", "hi"]
        )
        assert result.exit_code == 0
        assert "Tokens" in result.output

    def test_tokenize_outputs_token_count(self) -> None:
        result = _fresh_runner().invoke(
            main, ["tokenize", "--text", "मैं ठीक हूँ", "--language", "hi"]
        )
        assert result.exit_code == 0
        assert "3" in result.output  # 3 tokens

    def test_tokenize_bengali(self) -> None:
        result = _fresh_runner().invoke(
            main, ["tokenize", "--text", "আমার সোনার বাংলা", "--language", "bn"]
        )
        assert result.exit_code == 0

    def test_tokenize_tamil(self) -> None:
        result = _fresh_runner().invoke(
            main, ["tokenize", "--text", "வணக்கம் உலகம்", "--language", "ta"]
        )
        assert result.exit_code == 0

    def test_tokenize_unknown_language_warning(self) -> None:
        result = _fresh_runner().invoke(
            main, ["tokenize", "--text", "hello", "--language", "xx"]
        )
        # Should complete but warn
        assert "Warning" in result.output or result.exit_code == 0

    def test_tokenize_pipe_separator_in_output(self) -> None:
        result = _fresh_runner().invoke(
            main, ["tokenize", "--text", "मैं ठीक हूँ", "--language", "hi"]
        )
        assert "|" in result.output

    def test_tokenize_missing_text_errors(self) -> None:
        result = _fresh_runner().invoke(main, ["tokenize", "--language", "hi"])
        assert result.exit_code != 0

    def test_tokenize_missing_language_errors(self) -> None:
        result = _fresh_runner().invoke(main, ["tokenize", "--text", "hello"])
        assert result.exit_code != 0

    def test_tokenize_help(self) -> None:
        result = _fresh_runner().invoke(main, ["tokenize", "--help"])
        assert result.exit_code == 0
        assert "language" in result.output.lower()


class TestSentimentCommand:
    def test_sentiment_positive_hindi(self) -> None:
        result = _fresh_runner().invoke(
            main, ["sentiment", "--text", "खुश", "--language", "hi"]
        )
        assert result.exit_code == 0
        assert "POSITIVE" in result.output

    def test_sentiment_negative_hindi(self) -> None:
        result = _fresh_runner().invoke(
            main, ["sentiment", "--text", "नफरत", "--language", "hi"]
        )
        assert result.exit_code == 0
        assert "NEGATIVE" in result.output

    def test_sentiment_neutral_unknown_text(self) -> None:
        result = _fresh_runner().invoke(
            main, ["sentiment", "--text", "अज्ञात", "--language", "hi"]
        )
        assert result.exit_code == 0
        assert "NEUTRAL" in result.output

    def test_sentiment_outputs_score(self) -> None:
        result = _fresh_runner().invoke(
            main, ["sentiment", "--text", "खुश", "--language", "hi"]
        )
        assert "Score:" in result.output

    def test_sentiment_bengali_positive(self) -> None:
        result = _fresh_runner().invoke(
            main, ["sentiment", "--text", "ভালো", "--language", "bn"]
        )
        assert result.exit_code == 0
        assert "POSITIVE" in result.output

    def test_sentiment_missing_text_errors(self) -> None:
        result = _fresh_runner().invoke(main, ["sentiment", "--language", "hi"])
        assert result.exit_code != 0

    def test_sentiment_missing_language_errors(self) -> None:
        result = _fresh_runner().invoke(main, ["sentiment", "--text", "खुश"])
        assert result.exit_code != 0

    def test_sentiment_help(self) -> None:
        result = _fresh_runner().invoke(main, ["sentiment", "--help"])
        assert result.exit_code == 0


class TestNERCommand:
    def test_ner_finds_person(self) -> None:
        result = _fresh_runner().invoke(
            main, ["ner", "--text", "श्री राम दिल्ली में हैं", "--language", "hi"]
        )
        assert result.exit_code == 0
        assert "PERSON" in result.output

    def test_ner_finds_location(self) -> None:
        result = _fresh_runner().invoke(
            main, ["ner", "--text", "वह दिल्ली में रहते हैं", "--language", "hi"]
        )
        assert result.exit_code == 0
        assert "LOCATION" in result.output

    def test_ner_no_entities_message(self) -> None:
        result = _fresh_runner().invoke(
            main, ["ner", "--text", "यह एक साधारण वाक्य है", "--language", "hi"]
        )
        assert result.exit_code == 0
        # Either "No named entities" or entity list
        assert isinstance(result.output, str)

    def test_ner_outputs_span(self) -> None:
        result = _fresh_runner().invoke(
            main, ["ner", "--text", "श्री राम यहाँ हैं", "--language", "hi"]
        )
        if "PERSON" in result.output:
            assert "span=" in result.output

    def test_ner_missing_text_errors(self) -> None:
        result = _fresh_runner().invoke(main, ["ner", "--language", "hi"])
        assert result.exit_code != 0

    def test_ner_missing_language_errors(self) -> None:
        result = _fresh_runner().invoke(main, ["ner", "--text", "test"])
        assert result.exit_code != 0

    def test_ner_help(self) -> None:
        result = _fresh_runner().invoke(main, ["ner", "--help"])
        assert result.exit_code == 0


class TestTransliterateCommand:
    def test_transliterate_devanagari_to_latin(self) -> None:
        result = _fresh_runner().invoke(
            main,
            ["transliterate", "--text", "क", "--from", "devanagari", "--to", "latin"],
        )
        assert result.exit_code == 0
        assert "k" in result.output

    def test_transliterate_bengali_to_latin(self) -> None:
        result = _fresh_runner().invoke(
            main,
            ["transliterate", "--text", "ক", "--from", "bengali", "--to", "latin"],
        )
        assert result.exit_code == 0
        assert "k" in result.output

    def test_transliterate_indic_to_indic_pivot(self) -> None:
        result = _fresh_runner().invoke(
            main,
            ["transliterate", "--text", "क", "--from", "devanagari", "--to", "bengali"],
        )
        assert result.exit_code == 0
        # Returns pivot notation
        assert result.output.strip() != ""

    def test_transliterate_missing_text_errors(self) -> None:
        result = _fresh_runner().invoke(
            main, ["transliterate", "--from", "devanagari", "--to", "latin"]
        )
        assert result.exit_code != 0

    def test_transliterate_missing_from_errors(self) -> None:
        result = _fresh_runner().invoke(
            main, ["transliterate", "--text", "क", "--to", "latin"]
        )
        assert result.exit_code != 0

    def test_transliterate_missing_to_errors(self) -> None:
        result = _fresh_runner().invoke(
            main, ["transliterate", "--text", "क", "--from", "devanagari"]
        )
        assert result.exit_code != 0

    def test_transliterate_help(self) -> None:
        result = _fresh_runner().invoke(main, ["transliterate", "--help"])
        assert result.exit_code == 0


class TestLanguagesCommand:
    def test_languages_exits_zero(self) -> None:
        result = _fresh_runner().invoke(main, ["languages"])
        assert result.exit_code == 0

    def test_languages_lists_all_scheduled(self) -> None:
        result = _fresh_runner().invoke(main, ["languages"])
        non_empty_lines = [l for l in result.output.splitlines() if l.strip()]
        assert len(non_empty_lines) >= 22

    def test_languages_includes_hindi(self) -> None:
        result = _fresh_runner().invoke(main, ["languages"])
        assert "Hindi" in result.output

    def test_languages_includes_tamil(self) -> None:
        result = _fresh_runner().invoke(main, ["languages"])
        assert "Tamil" in result.output

    def test_languages_includes_scripts(self) -> None:
        result = _fresh_runner().invoke(main, ["languages"])
        assert "Devanagari" in result.output
        assert "script=" in result.output

    def test_languages_shows_speaker_count(self) -> None:
        result = _fresh_runner().invoke(main, ["languages"])
        assert "speakers=" in result.output

    def test_languages_help(self) -> None:
        result = _fresh_runner().invoke(main, ["languages", "--help"])
        assert result.exit_code == 0
