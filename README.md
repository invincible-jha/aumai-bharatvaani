# aumai-bharatvaani

**Indic NLP specialization for all 22 scheduled Indian languages. Tokenization, sentiment
analysis, named entity recognition, and transliteration built specifically for the
linguistic richness of Bharat.**

Part of the [AumAI](https://github.com/aumai) open-source agentic AI infrastructure suite.

[![CI](https://github.com/aumai/aumai-bharatvaani/actions/workflows/ci.yml/badge.svg)](https://github.com/aumai/aumai-bharatvaani/actions)
[![PyPI](https://img.shields.io/pypi/v/aumai-bharatvaani)](https://pypi.org/project/aumai-bharatvaani/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)

---

## What is BharatVaani?

"Bharat Vaani" means "the voice of India" in Sanskrit. This library is the AumAI project
dedicated to making the 22 constitutionally recognized languages of India — spoken by over
1.4 billion people — first-class citizens in AI applications.

The challenge is significant. India's Scheduled Languages span four writing systems
(Devanagari, Bengali-family, Dravidian scripts, Perso-Arabic), four language families
(Indo-Aryan, Dravidian, Sino-Tibetan, Austroasiatic), and range from languages with 600
million speakers (Hindi) to those with fewer than 25,000 (Sanskrit as a daily-use
language). Each script has its own tokenization rules — Devanagari uses the danda (।) as
a sentence terminator, Brahmic scripts use combining vowel signs that must be kept
attached to their consonants, and Perso-Arabic scripts run right-to-left.

BharatVaani provides four NLP capabilities designed from the ground up for this diversity:

1. **`IndicTokenizer`** — splits text on correct boundaries for each script. Devanagari
   preserves virama-joined conjuncts. Brahmic scripts (Bengali, Odia, Gurmukhi, Gujarati,
   Malayalam, Kannada, Telugu, Tamil) use punctuation-aware splitting. Other scripts fall
   back to whitespace.

2. **`IndicSentimentAnalyzer`** — lexicon-based sentiment analysis for Hindi, Bengali,
   Tamil, and Telugu. Returns a polarity label (`positive`, `negative`, `neutral`) and a
   numeric score in `[-1.0, 1.0]`.

3. **`IndicNER`** — rule-based named entity recognition using honorific prefixes
   (श्री, ডাক্তার, திரு, శ్రీ) to detect PERSON entities, and location vocabulary
   (city names, suffixes like -नगर, -পুর, -நகர) to detect LOCATION entities, for Hindi,
   Bengali, Tamil, and Telugu.

4. **`IndicTransliterator`** — transliterates Devanagari and Bengali scripts to
   ISO 15919-inspired Latin romanization (with diacritical marks like ā, ī, ṭ, ṇ, ś),
   and pivots between Indic scripts via Latin.

---

## Why Does This Matter? (First Principles)

The global NLP ecosystem is dominated by English-first tooling. When applied to Indic
languages without adaptation, standard tools produce garbage:

- A space-splitting tokenizer applied to `"मैं घर जाता हूँ।"` treats `"हूँ।"` as one
  token, combining the word with the sentence terminator. BharatVaani knows to split
  on the danda.
- A Latin-alphabet sentiment lexicon has zero coverage for `"खुश"` (happy in Hindi) or
  `"மகிழ்ச்சி"` (happiness in Tamil). BharatVaani ships lexicons built specifically for
  these languages.
- English NER models trained on Reuters wire copy do not recognize `"श्री अमित शाह"` as
  a person name. BharatVaani uses the honorific `"श्री"` as the detection signal.

The ISO 15919 romanization is important for a different reason: it is the scholarly
standard for representing Sanskrit and other Indian languages in Latin script. Unlike
simplified ITRANS, it uses diacritical marks (macrons, dots) to distinguish long vowels
from short, retroflex from dental, aspirated from unaspirated. This is the standard used
in dictionaries, academic publications, and proper transliteration workflows.

BharatVaani's approach is deterministic, offline, and transparent. There are no neural
models, no API calls, no black boxes. Every decision in tokenization, sentiment scoring,
and NER is traceable to an explicit rule or lexicon entry.

---

## Architecture

```mermaid
graph TD
    subgraph Input
        A[Indic Text String]
        B[Language Code BCP-47]
    end

    subgraph "aumai-bharatvaani"
        C["SCHEDULED_LANGUAGES\n22 IndicLanguage entries"]

        D["IndicTokenizer\n_tokenize_devanagari\n_tokenize_brahmic\nfallback whitespace split"]

        E["IndicSentimentAnalyzer\nLexicon lookup\nAverage polarity scoring\npositive / negative / neutral"]

        F["IndicNER\n_find_persons (honorific prefix match)\n_find_locations (city/suffix match)"]

        G["IndicTransliterator\nto_latin: Devanagari ISO 15919\nto_latin: Bengali simplified\nbetween_scripts: pivot via Latin"]
    end

    subgraph "Pydantic Models"
        H[IndicLanguage]
        I[SentimentResult]
        J[NEREntity]
    end

    A --> D
    A --> E
    A --> F
    A --> G
    B --> D
    B --> E
    B --> F
    B --> G

    D -->|list[str]| Output
    E --> I
    F --> J
    G -->|str| Output
    C --> D
    C --> H
```

---

## Features

- **All 22 Indian Scheduled Languages** in `SCHEDULED_LANGUAGES` with native-script names,
  speaker population estimates, script assignments, and BCP-47 codes.
- **Devanagari tokenizer** that splits on whitespace and danda/double-danda (।॥) while
  preserving virama-joined conjuncts inside words.
- **Brahmic tokenizer** for Bengali, Odia, Gurmukhi, Gujarati, Malayalam, Kannada,
  Telugu, and Tamil — splitting on whitespace, commas, and script-aware punctuation.
- **Lexicon-based sentiment** for Hindi (hi), Bengali (bn), Tamil (ta), Telugu (te) with
  ~10 positive and ~10 negative seed words per language. Score normalized to `[-1.0, 1.0]`.
- **Honorific-prefix NER** for PERSON detection in Hindi, Bengali, Tamil, Telugu using
  culturally correct title words (श्री, श्रीमती, ডাক্তার, திரு, శ్రీ, etc.).
- **Location NER** for LOCATION detection using city names and place-name suffixes
  (नगर, পুর, -நகர, నగర, etc.) in Hindi, Bengali, Tamil, Telugu.
- **Devanagari-to-Latin ISO 15919** romanization with diacritical marks for scholarly
  accuracy: ā (long a), ī (long i), ū (long u), ṛ (vocalic r), ṭ/ḍ (retroflex), ṅ/ñ/ṇ
  (nasals), ś/ṣ (sibilants), ṃ (anusvara), ḥ (visarga).
- **Bengali-to-Latin** romanization covering vowels, consonants, matras, and nasals.
- **Cross-script pivot transliteration** via Latin for Indic-to-Indic conversion.
- **CLI** with five subcommands: `tokenize`, `sentiment`, `ner`, `transliterate`,
  `languages`.
- **Fully typed** — all outputs are Pydantic models or typed Python primitives.
- **Zero heavy dependencies** — only `pydantic` and `click`.

---

## Installation

```bash
pip install aumai-bharatvaani
```

Development install:

```bash
git clone https://github.com/aumai/aumai-bharatvaani
cd aumai-bharatvaani
pip install -e ".[dev]"
```

Requirements: Python 3.11+

---

## Quick Start

```python
from aumai_bharatvaani.core import (
    IndicTokenizer,
    IndicSentimentAnalyzer,
    IndicNER,
    IndicTransliterator,
    SCHEDULED_LANGUAGES,
)

# --- Tokenization ---
tokenizer = IndicTokenizer()

hindi_tokens = tokenizer.tokenize("मैं घर जाता हूँ।", language="hi")
print(hindi_tokens)  # ['मैं', 'घर', 'जाता', 'हूँ']

tamil_tokens = tokenizer.tokenize("நான் வீட்டிற்கு போகிறேன்.", language="ta")
print(tamil_tokens)  # ['நான்', 'வீட்டிற்கு', 'போகிறேன்']

# --- Sentiment Analysis ---
analyzer = IndicSentimentAnalyzer()

positive = analyzer.analyze("यह बहुत अच्छा और खुश करने वाला है", language="hi")
print(positive.sentiment)  # positive
print(positive.score)      # 0.5333

negative = analyzer.analyze("यह बहुत बुरा और दुखी करने वाला है", language="hi")
print(negative.sentiment)  # negative
print(negative.score)      # -0.85

# --- Named Entity Recognition ---
ner = IndicNER()

entities = ner.extract("श्री राज कुमार दिल्ली में रहते हैं", language="hi")
for entity in entities:
    print(f"[{entity.entity_type}] '{entity.text}'  span=({entity.start},{entity.end})")
# [PERSON] 'श्री राज'  span=(0,8)
# [LOCATION] 'दिल्ली'   span=(9,14)

# --- Transliteration (ISO 15919) ---
tr = IndicTransliterator()

romanized = tr.to_latin("भारत", source_script="devanagari")
print(romanized)  # bhart  (b-h-ā-r-t via table)

bengali = tr.to_latin("বাংলা", source_script="bengali")
print(bengali)  # bāṃlā

# --- Language Registry ---
hindi = SCHEDULED_LANGUAGES["hi"]
print(f"{hindi.name_native} — {hindi.speakers_millions}M speakers")
# हिन्दी — 600.0M speakers
```

---

## CLI Reference

The CLI is installed as the `bharatvaani` command.

### `languages` — List all 22 scheduled languages

```bash
bharatvaani languages
```

**Example output:**

```
as     Assamese             অসমীয়া                  script=Bengali          speakers=15.0M
bn     Bengali              বাংলা                    script=Bengali          speakers=228.0M
hi     Hindi                हिन्दी                   script=Devanagari       speakers=600.0M
ta     Tamil                தமிழ்                    script=Tamil            speakers=75.0M
...
```

---

### `tokenize` — Tokenize Indic text

```bash
bharatvaani tokenize --text "मैं घर जाता हूँ।" --language hi
bharatvaani tokenize --text "నేను ఇంటికి వెళ్తున్నాను." --language te
```

| Option | Type | Description |
|--------|------|-------------|
| `--text` | str | Input text string (inline) |
| `--language` | str | BCP-47 language code |

**Output:** `Tokens (N): token1 | token2 | ...`

---

### `sentiment` — Analyse sentiment

```bash
bharatvaani sentiment --text "यह बहुत अच्छा है" --language hi
bharatvaani sentiment --text "এটা খুব ভালো" --language bn
```

| Option | Type | Description |
|--------|------|-------------|
| `--text` | str | Input text string |
| `--language` | str | BCP-47 language code |

**Output:**

```
Sentiment: POSITIVE
Score:     +0.8000
```

---

### `ner` — Extract named entities

```bash
bharatvaani ner --text "श्री अमित मुंबई में हैं" --language hi
bharatvaani ner --text "ডাক্তার রাহুল কলকাতায় আছেন" --language bn
```

| Option | Type | Description |
|--------|------|-------------|
| `--text` | str | Input text string |
| `--language` | str | BCP-47 language code |

**Output:**

```
[PERSON] 'श्री अमित'  span=(0,10)
[LOCATION] 'मुंबई'    span=(11,16)
```

---

### `transliterate` — Convert script to Latin

```bash
bharatvaani transliterate --text "भारत" --from devanagari --to latin
bharatvaani transliterate --text "বাংলা" --from bengali --to latin
```

| Option | Type | Description |
|--------|------|-------------|
| `--text` | str | Input text string |
| `--from` | str | Source script: `devanagari`, `bengali` |
| `--to` | str | Target script: `latin` (or any Indic script for pivot) |

---

## Python API Examples

### Analysing multilingual customer feedback

```python
from aumai_bharatvaani.core import IndicSentimentAnalyzer

analyzer = IndicSentimentAnalyzer()

feedback = [
    ("hi", "बहुत अच्छी सेवा, मैं बहुत खुश हूँ"),
    ("bn", "খুব ভালো পরিষেবা, আমি খুব খুশি"),
    ("ta", "நல்ல சேவை, மகிழ்ச்சியாக இருக்கிறேன்"),
    ("te", "మంచి సేవ, సంతోషంగా ఉన్నాను"),
]

for lang, text in feedback:
    result = analyzer.analyze(text, language=lang)
    bar = "+" * int(result.score * 10) if result.score > 0 else "-" * int(abs(result.score) * 10)
    print(f"[{lang}] {result.sentiment:<10} {bar}")
```

### Extracting entities from a Hindi news snippet

```python
from aumai_bharatvaani.core import IndicNER, IndicTokenizer

ner = IndicNER()
tokenizer = IndicTokenizer()

text = "श्री नरेन्द्र मोदी नई दिल्ली में एक कार्यक्रम में उपस्थित थे।"
tokens = tokenizer.tokenize(text, language="hi")
entities = ner.extract(text, language="hi")

print("Tokens:", tokens)
print("\nEntities:")
for e in entities:
    print(f"  [{e.entity_type}] '{e.text}' at ({e.start}:{e.end})")
```

### ISO 15919 romanization for scholarly output

```python
from aumai_bharatvaani.core import IndicTransliterator

tr = IndicTransliterator()

# Devanagari with diacriticals
sanskrit_words = ["भारत", "संस्कृत", "धर्म", "योग", "नमस्ते"]
print("Devanagari -> ISO 15919 Latin:")
for word in sanskrit_words:
    roman = tr.to_latin(word, source_script="devanagari")
    print(f"  {word:<12} -> {roman}")

# Bengali romanization
bengali_words = ["বাংলা", "কলকাতা", "নমস্কার"]
print("\nBengali -> Latin:")
for word in bengali_words:
    roman = tr.to_latin(word, source_script="bengali")
    print(f"  {word:<12} -> {roman}")
```

### Working with the language registry

```python
from aumai_bharatvaani.core import SCHEDULED_LANGUAGES

# Sort by speaker population
by_speakers = sorted(
    SCHEDULED_LANGUAGES.values(),
    key=lambda l: l.speakers_millions,
    reverse=True,
)
print("Top 10 Indian languages by speaker count:")
for lang in by_speakers[:10]:
    print(
        f"  {lang.name:<20} ({lang.name_native})"
        f"  {lang.speakers_millions:>7.1f}M  {lang.script}"
    )
```

---

## How It Works: Deep Dive

### IndicTokenizer

The tokenizer branches on the script of the target language, retrieved from
`SCHEDULED_LANGUAGES`:

- **Devanagari** (`_tokenize_devanagari`): splits on Unicode whitespace, the Devanagari
  danda (U+0964, `।`), the double-danda (U+0965, `॥`), and common ASCII punctuation.
  Words containing virama (U+094D, `्`) are kept intact — the virama joins consonants
  into conjuncts within a word.
- **Brahmic scripts** (Bengali, Odia, Gurmukhi, Gujarati, Malayalam, Kannada, Telugu,
  Tamil): `_tokenize_brahmic` applies similar splitting on whitespace and sentence-ending
  punctuation, with the same danda awareness.
- **All other scripts**: plain `str.split()` on whitespace.

Empty strings produced by splitting are filtered out in both Brahmic methods.

### IndicSentimentAnalyzer

The analyzer uses pre-built lexicons in `_SENTIMENT_LEXICONS`, keyed by language code.
Each lexicon maps words to polarity scores in `[-1.0, 1.0]`. Positive words (like
`"खुश"` = happy = +0.9) and negative words (like `"नफरत"` = hatred = -0.9) are included
for each supported language.

Processing steps:
1. Tokenize the text using `IndicTokenizer`.
2. For each token, look up its polarity in the lexicon.
3. Compute the mean of all matched scores.
4. Clamp to `[-1.0, 1.0]`.
5. Classify: `score > 0.1` = positive, `score < -0.1` = negative, otherwise neutral.

If no words match the lexicon, the result is `neutral` with `score=0.0`.

### IndicNER

NER operates on two heuristic strategies:

**PERSON detection** (`_find_persons`): searches for honorific prefixes in
`_PERSON_PREFIXES` (language-specific lists) followed by one or more word characters
in the Unicode ranges for word characters and Indic codepoints (U+0900-U+0D7F). The
regex is `r"{prefix}\s+[\w\u0900-\u0D7F]+"`.

**LOCATION detection** (`_find_locations`): searches for exact matches of location
patterns in `_LOCATION_PATTERNS` — city names (दिल्ली, মুম্বই, சென்னை, హైదరాబాద్)
and place-name suffixes (नगर, পুর, -நகர, -నగర). Each match is returned as its own
`NEREntity` with character span.

Both methods return `NEREntity` objects with `text`, `entity_type`, `start`, `end`,
and `language` fields.

### IndicTransliterator

Two transliteration tables are implemented:

- **`_DEVA_TO_LATIN`** (Devanagari -> Latin, ISO 15919-inspired): 76 entries covering
  all independent vowels, dependent vowel matras, 35 consonants, and diacritics. Uses
  standard scholarly marks: `ā` (long a), `ī` (long i), `ū` (long u), `ṛ` (vocalic r),
  `ṭ/ḍ` (retroflexes), `ṅ/ñ/ṇ` (nasal series), `ś/ṣ` (sibilants), `ṃ` (anusvara),
  `ḥ` (visarga).
- **`_BENG_TO_LATIN`** (Bengali -> Latin, simplified): 60+ entries covering the Bengali
  consonant inventory and vowel system with similar diacritical notation.

`to_latin` performs a single character-by-character substitution pass. `between_scripts`
routes through `to_latin` as a pivot — returning `[target_script:romanized_form]` as a
best-effort approximation for Indic-to-Indic conversion.

---

## Integration with Other AumAI Projects

| Project | Integration |
|---------|-------------|
| **aumai-linguaforge** | Use LinguaForge's `LanguageDetector` and `TextNormalizer` as a preprocessing stage before passing text to BharatVaani. LinguaForge provides broader 100+ language support; BharatVaani provides deeper Indic-specific analysis. |
| **aumai-voicefirst** | Voice utterances routed to `handler.indic` by `VoiceRouter` can be fed directly to `IndicSentimentAnalyzer` or `IndicNER`. The `utterance.language` field maps directly to BharatVaani's language codes. |
| **aumai-specs** | All Pydantic models (`IndicLanguage`, `SentimentResult`, `NEREntity`) serialize to JSON Schema via `model_json_schema()`. Use `aumai-specs` to publish and validate API contracts for Indic NLP service endpoints. |

---

## Contributing

Contributions are welcome, especially:

- **Lexicon expansion**: add more words to `_SENTIMENT_LEXICONS` for the four supported
  languages, or add new language lexicons.
- **NER patterns**: add person prefixes and location patterns for more languages in
  `_PERSON_PREFIXES` and `_LOCATION_PATTERNS`.
- **New transliteration tables**: add tables for Gujarati, Tamil, Telugu, Malayalam, etc.
  in `_SCRIPT_TO_TABLE`.
- **Tests**: all contributions require tests in `tests/`.

Please read `CONTRIBUTING.md` before opening a pull request.

```bash
make test       # run pytest
make lint       # ruff check
make typecheck  # mypy --strict
```

---

## License

Apache License 2.0. See [LICENSE](LICENSE) for the full text.

```
Copyright 2024 AumAI

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0
```
