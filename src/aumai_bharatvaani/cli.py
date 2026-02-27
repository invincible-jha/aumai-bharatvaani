"""CLI entry point for aumai-bharatvaani."""

from __future__ import annotations

import sys

import click

from aumai_bharatvaani.core import (
    IndicNER,
    IndicSentimentAnalyzer,
    IndicTokenizer,
    IndicTransliterator,
    SCHEDULED_LANGUAGES,
)

_tokenizer = IndicTokenizer()
_sentiment = IndicSentimentAnalyzer()
_ner = IndicNER()
_transliterator = IndicTransliterator()


@click.group()
@click.version_option()
def main() -> None:
    """AumAI BharatVaani — Indic NLP specialization CLI."""


@main.command("tokenize")
@click.option("--text", required=True, help="Input text string.")
@click.option("--language", required=True, help="BCP-47 language code (e.g. hi, ta, bn).")
def tokenize(text: str, language: str) -> None:
    """Tokenize Indic text."""
    if language not in SCHEDULED_LANGUAGES:
        click.echo(f"Warning: '{language}' is not a recognized scheduled language.", err=True)
    tokens = _tokenizer.tokenize(text, language=language)
    click.echo(f"Tokens ({len(tokens)}): {' | '.join(tokens)}")


@main.command("sentiment")
@click.option("--text", required=True, help="Input text string.")
@click.option("--language", required=True, help="BCP-47 language code.")
def sentiment(text: str, language: str) -> None:
    """Analyse sentiment of Indic text."""
    result = _sentiment.analyze(text, language=language)
    click.echo(f"Sentiment: {result.sentiment.upper()}")
    click.echo(f"Score:     {result.score:+.4f}")


@main.command("ner")
@click.option("--text", required=True, help="Input text string.")
@click.option("--language", required=True, help="BCP-47 language code.")
def ner(text: str, language: str) -> None:
    """Extract named entities from Indic text."""
    entities = _ner.extract(text, language=language)
    if not entities:
        click.echo("No named entities found.")
        return
    for entity in entities:
        click.echo(
            f"[{entity.entity_type}] '{entity.text}'  "
            f"span=({entity.start},{entity.end})"
        )


@main.command("transliterate")
@click.option("--text", required=True, help="Input text string.")
@click.option("--from", "source_script", required=True, help="Source script (e.g. devanagari, bengali).")
@click.option("--to", "target_script", required=True, help="Target script (e.g. latin).")
def transliterate(text: str, source_script: str, target_script: str) -> None:
    """Transliterate Indic text between scripts."""
    try:
        if target_script.lower() == "latin":
            result = _transliterator.to_latin(text, source_script)
        else:
            result = _transliterator.between_scripts(text, source=source_script, target=target_script)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    click.echo(result)


@main.command("languages")
def languages() -> None:
    """List all 22 Indian scheduled languages."""
    for code, lang in sorted(SCHEDULED_LANGUAGES.items()):
        click.echo(
            f"{lang.code:<6} {lang.name:<20} {lang.name_native:<24} "
            f"script={lang.script:<15} speakers={lang.speakers_millions:.1f}M"
        )


if __name__ == "__main__":
    main()
