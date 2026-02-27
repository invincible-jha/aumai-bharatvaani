"""Quickstart examples for aumai-bharatvaani.

Demonstrates five independent capabilities of the library:
  1. Listing all supported Indic languages
  2. Tokenizing Indic text (Hindi and Tamil)
  3. Sentiment analysis across multiple languages
  4. Named entity recognition in Hindi text
  5. Script transliteration (Devanagari and Bengali to Latin)

Run this file directly to see all demonstrations:

    python examples/quickstart.py

Disclaimer: This tool provides NLP capabilities for Indic languages.
Verify results with native speakers before using them in production.
"""

from __future__ import annotations

from aumai_bharatvaani.core import (
    SCHEDULED_LANGUAGES,
    IndicNER,
    IndicSentimentAnalyzer,
    IndicTokenizer,
    IndicTransliterator,
)
from aumai_bharatvaani.models import NEREntity, SentimentResult


# ---------------------------------------------------------------------------
# Demo 1 — List all 22 Indian scheduled languages
# ---------------------------------------------------------------------------


def demo_languages() -> None:
    """Print a formatted table of all 22 Indian scheduled languages.

    Each row shows the BCP-47 code, English name, native name, script family,
    and approximate speaker count in millions.
    """
    print("=" * 70)
    print("Demo 1: Supported Indic Languages")
    print("=" * 70)

    # SCHEDULED_LANGUAGES is a dict[str, IndicLanguage] sorted by code.
    for code, lang in sorted(SCHEDULED_LANGUAGES.items()):
        print(
            f"  {lang.code:<6} {lang.name:<20} {lang.name_native:<24} "
            f"script={lang.script:<15} speakers={lang.speakers_millions:.1f}M"
        )

    # Demonstrate metadata access on a specific language
    hindi = SCHEDULED_LANGUAGES["hi"]
    print(f"\nHindi details: code={hindi.code!r}, script={hindi.script!r}")
    print()


# ---------------------------------------------------------------------------
# Demo 2 — Tokenize Indic text
# ---------------------------------------------------------------------------


def demo_tokenization() -> None:
    """Tokenize Hindi and Tamil text using the script-aware IndicTokenizer.

    The tokenizer uses different splitting rules depending on the script family:
    - Devanagari: splits on whitespace and danda punctuation (। ॥)
    - Brahmic (Tamil, Telugu, etc.): similar whitespace-and-punctuation split
    """
    print("=" * 70)
    print("Demo 2: Tokenization")
    print("=" * 70)

    tokenizer = IndicTokenizer()

    # Hindi (Devanagari script)
    hindi_text = "नमस्ते भारत। यह एक परीक्षण है।"
    hindi_tokens = tokenizer.tokenize(hindi_text, language="hi")
    print(f"  Hindi input:  {hindi_text!r}")
    print(f"  Tokens ({len(hindi_tokens)}): {' | '.join(hindi_tokens)}")

    # Tamil (Tamil script — Brahmic family)
    tamil_text = "வணக்கம் தமிழ்நாடு. இது ஒரு சோதனை."
    tamil_tokens = tokenizer.tokenize(tamil_text, language="ta")
    print(f"\n  Tamil input:  {tamil_text!r}")
    print(f"  Tokens ({len(tamil_tokens)}): {' | '.join(tamil_tokens)}")

    # Bengali (Bengali script)
    bengali_text = "আমি বাংলা ভালোবাসি।"
    bengali_tokens = tokenizer.tokenize(bengali_text, language="bn")
    print(f"\n  Bengali input:  {bengali_text!r}")
    print(f"  Tokens ({len(bengali_tokens)}): {' | '.join(bengali_tokens)}")
    print()


# ---------------------------------------------------------------------------
# Demo 3 — Sentiment analysis across multiple languages
# ---------------------------------------------------------------------------


def demo_sentiment() -> None:
    """Run sentiment analysis on positive and negative samples in four languages.

    The lexicon-based analyser returns a SentimentResult with:
    - sentiment: "positive", "negative", or "neutral"
    - score: float in [-1.0, 1.0] (positive values = positive sentiment)

    Built-in lexicons cover Hindi (hi), Bengali (bn), Tamil (ta), Telugu (te).
    """
    print("=" * 70)
    print("Demo 3: Sentiment Analysis")
    print("=" * 70)

    analyzer = IndicSentimentAnalyzer()

    # Pairs of (text, language_code, expected_polarity)
    samples: list[tuple[str, str]] = [
        ("यह बहुत अच्छा और शानदार है।", "hi"),     # Hindi — positive
        ("यह बहुत बुरा और बेकार है।", "hi"),        # Hindi — negative
        ("এটি সুন্দর এবং ভালো।", "bn"),             # Bengali — positive
        ("இது நல்ல மகிழ்ச்சியான விஷயம்.", "ta"),   # Tamil — positive
        ("ఇది మంచి మరియు సంతోషంగా ఉంది.", "te"),  # Telugu — positive
    ]

    results: list[SentimentResult] = [
        analyzer.analyze(text, language=lang)
        for text, lang in samples
    ]

    for result in results:
        print(
            f"  [{result.language}] {result.sentiment:>8} "
            f"({result.score:+.4f}): {result.text}"
        )
    print()


# ---------------------------------------------------------------------------
# Demo 4 — Named entity recognition
# ---------------------------------------------------------------------------


def demo_ner() -> None:
    """Extract named entities from Hindi text using the rule-based IndicNER.

    The engine detects:
    - PERSON: words preceded by honorifics like श्री, श्रीमती, डॉ
    - LOCATION: known city names and location keywords

    Results are NEREntity objects with text, entity_type, start, and end.
    """
    print("=" * 70)
    print("Demo 4: Named Entity Recognition (NER)")
    print("=" * 70)

    ner = IndicNER()

    text = "डॉ प्रिया मुंबई में रहती हैं और श्री राम कोलकाता गए।"
    print(f"  Input: {text!r}")
    print()

    entities: list[NEREntity] = ner.extract(text, language="hi")

    if not entities:
        print("  No entities found.")
    else:
        for entity in entities:
            # Show the entity type, surface text, and its character span
            snippet = text[entity.start:entity.end]
            print(
                f"  [{entity.entity_type:<10}] '{entity.text}'  "
                f"span=({entity.start},{entity.end})  "
                f"extracted='{snippet}'"
            )

    # Also demonstrate filtering by entity type
    persons   = [e for e in entities if e.entity_type == "PERSON"]
    locations = [e for e in entities if e.entity_type == "LOCATION"]
    print(f"\n  Persons ({len(persons)}):   {[e.text for e in persons]}")
    print(f"  Locations ({len(locations)}): {[e.text for e in locations]}")
    print()


# ---------------------------------------------------------------------------
# Demo 5 — Script transliteration
# ---------------------------------------------------------------------------


def demo_transliteration() -> None:
    """Transliterate Devanagari and Bengali text to Latin romanization.

    Uses an ISO 15919 / ITRANS approximation. Characters not in the table
    pass through unchanged. Indic-to-Indic conversion pivots via Latin.

    Supported source scripts: "devanagari", "bengali"
    """
    print("=" * 70)
    print("Demo 5: Script Transliteration")
    print("=" * 70)

    t = IndicTransliterator()

    # Devanagari words to Latin
    devanagari_words = ["नमस्ते", "भारत", "धन्यवाद", "स्वागत", "संस्कृत"]
    print("  Devanagari -> Latin:")
    for word in devanagari_words:
        latin = t.to_latin(word, source_script="devanagari")
        print(f"    {word} -> {latin!r}")

    # Bengali words to Latin
    print()
    bengali_words = ["বাংলা", "ধন্যবাদ", "আমার", "সুন্দর"]
    print("  Bengali -> Latin:")
    for word in bengali_words:
        latin = t.to_latin(word, source_script="bengali")
        print(f"    {word} -> {latin!r}")

    # Pivot-based cross-script transliteration (experimental)
    print()
    pivot = t.between_scripts("नमस्ते", source="devanagari", target="tamil")
    print(f"  Devanagari -> Tamil (pivot): {pivot!r}")

    # Demonstrate ValueError for unsupported scripts
    print()
    try:
        t.to_latin("hello", source_script="gujarati")
    except ValueError as exc:
        print(f"  Expected error for unsupported script: {exc}")
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Run all five quickstart demonstrations in sequence."""
    print("\nAumAI BharatVaani — Quickstart")
    print(
        "Disclaimer: Verify NLP results with native speakers "
        "before production use.\n"
    )

    demo_languages()
    demo_tokenization()
    demo_sentiment()
    demo_ner()
    demo_transliteration()

    print("All demos complete.")


if __name__ == "__main__":
    main()
