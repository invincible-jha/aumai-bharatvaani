# Getting Started with AumAI BharatVaani

> **Disclaimer:** This tool provides NLP capabilities for Indic languages. Verify translations and
> linguistic analysis results with native speakers before using them in production contexts.

AumAI BharatVaani is an open-source Python library for natural language processing across all 22
Indian scheduled languages. It provides tokenization, sentiment analysis, named entity recognition
(NER), and script transliteration — all with no external model dependencies for the core
functionality.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Step-by-Step Tutorial](#step-by-step-tutorial)
4. [Five Common Patterns](#five-common-patterns)
5. [Troubleshooting FAQ](#troubleshooting-faq)

---

## Prerequisites

| Requirement | Minimum version | Notes |
|-------------|-----------------|-------|
| Python | 3.11 | Run `python3 --version` to check |
| pip | 23.x | Ships with Python |
| tiktoken | optional | Not used by BharatVaani itself |

BharatVaani's core features run with **zero mandatory third-party dependencies** beyond Pydantic.
Installing the package via `pip` will pull in Pydantic automatically.

---

## Installation

### From PyPI (recommended)

```bash
pip install aumai-bharatvaani
```

### From source

```bash
git clone https://github.com/aumai/aumai-bharatvaani.git
cd aumai-bharatvaani
pip install -e ".[dev]"
```

### Verify the installation

```bash
python -c "import aumai_bharatvaani; print('OK')"
aumai-bharatvaani --version
```

---

## Step-by-Step Tutorial

This tutorial walks through each NLP capability using Hindi (`hi`) as the primary example.
All capabilities work identically for the other 21 scheduled languages where lexicon data exists.

### Step 1 — List supported languages

Before processing text, check which language codes BharatVaani recognises. Each entry in
`SCHEDULED_LANGUAGES` is an `IndicLanguage` object with a BCP-47 code, English name, native-script
name, script family, and speaker count.

```python
from aumai_bharatvaani.core import SCHEDULED_LANGUAGES

for code, lang in sorted(SCHEDULED_LANGUAGES.items()):
    print(
        f"{lang.code:<6} {lang.name:<20} {lang.name_native:<24} "
        f"script={lang.script}"
    )
```

From the command line:

```bash
aumai-bharatvaani languages
```

Sample output:

```
as     Assamese             অসমীয়া                  script=Bengali
bn     Bengali              বাংলা                    script=Bengali
hi     Hindi                हिन्दी                   script=Devanagari
ta     Tamil                தமிழ்                    script=Tamil
...
```

### Step 2 — Tokenize Indic text

Tokenization splits raw text into individual words. BharatVaani uses script-aware rules:
Devanagari text is split on whitespace and punctuation marks (`।` U+0964 and `॥` U+0965);
other Brahmic scripts (Bengali, Tamil, Telugu, etc.) receive similar treatment.

```python
from aumai_bharatvaani.core import IndicTokenizer

tokenizer = IndicTokenizer()

# Hindi example
tokens = tokenizer.tokenize(
    "नमस्ते भारत। यह एक परीक्षण है।",
    language="hi",
)
print(tokens)
# ['नमस्ते', 'भारत', 'यह', 'एक', 'परीक्षण', 'है']

# Tamil example
tokens_ta = tokenizer.tokenize("வணக்கம் தமிழ்நாடு.", language="ta")
print(tokens_ta)
# ['வணக்கம்', 'தமிழ்நாடு']
```

From the command line:

```bash
aumai-bharatvaani tokenize \
    --text "नमस्ते भारत। यह एक परीक्षण है।" \
    --language hi
```

### Step 3 — Analyse sentiment

Sentiment analysis returns whether text is positive, negative, or neutral, along with a numeric
score in the range [-1.0, 1.0]. Positive values indicate positive sentiment.

```python
from aumai_bharatvaani.core import IndicSentimentAnalyzer

analyzer = IndicSentimentAnalyzer()

result = analyzer.analyze(
    "यह बहुत अच्छा है और मुझे बहुत खुशी है।",
    language="hi",
)
print(result.sentiment)  # "positive"
print(result.score)      # e.g. 0.6333
print(result.language)   # "hi"
```

The return value is a `SentimentResult` Pydantic model. See [API Reference](api-reference.md)
for the full field list.

From the command line:

```bash
aumai-bharatvaani sentiment \
    --text "यह बहुत अच्छा है" \
    --language hi
```

### Step 4 — Extract named entities

Named Entity Recognition identifies people, places, and organisations. BharatVaani uses rule-based
heuristics: honorific prefixes detect persons (e.g. `श्री`, `डॉ`), and known city/location
keywords detect locations.

```python
from aumai_bharatvaani.core import IndicNER

ner = IndicNER()
entities = ner.extract("श्री राज दिल्ली में हैं।", language="hi")

for entity in entities:
    print(
        f"[{entity.entity_type}] '{entity.text}'  "
        f"span=({entity.start},{entity.end})"
    )
# [PERSON]   'श्री राज'   span=(0,9)
# [LOCATION] 'दिल्ली'     span=(10,16)
```

From the command line:

```bash
aumai-bharatvaani ner \
    --text "श्री राज दिल्ली में हैं।" \
    --language hi
```

### Step 5 — Transliterate scripts

Transliteration converts text from one writing system to another. BharatVaani supports Devanagari
and Bengali to Latin (ISO 15919 approximation), and pivot-based conversion between Indic scripts.

```python
from aumai_bharatvaani.core import IndicTransliterator

t = IndicTransliterator()

# Devanagari to Latin
print(t.to_latin("नमस्ते", source_script="devanagari"))
# "namaste"

# Bengali to Latin
print(t.to_latin("বাংলা", source_script="bengali"))
# "bāṃlā"

# Devanagari to Bengali (pivot via Latin)
print(t.between_scripts("नमस्ते", source="devanagari", target="bengali"))
# "[bengali:namaste]"
```

From the command line:

```bash
aumai-bharatvaani transliterate \
    --text "नमस्ते" \
    --from devanagari \
    --to latin
```

---

## Five Common Patterns

### Pattern 1 — Batch sentiment analysis across multiple languages

```python
from aumai_bharatvaani.core import IndicSentimentAnalyzer
from aumai_bharatvaani.models import SentimentResult

analyzer = IndicSentimentAnalyzer()

texts = [
    ("यह बहुत अच्छा है।",       "hi"),
    ("এটি সুন্দর।",               "bn"),
    ("இது நல்ல விஷயம்.",         "ta"),
    ("ఇది మంచిది.",               "te"),
]

results: list[SentimentResult] = [
    analyzer.analyze(text, language=lang)
    for text, lang in texts
]

for result in results:
    print(
        f"[{result.language}] {result.sentiment:>8} "
        f"({result.score:+.4f}): {result.text}"
    )
```

### Pattern 2 — Filter named entities by type

```python
from aumai_bharatvaani.core import IndicNER

ner = IndicNER()
text = "डॉ प्रिया मुंबई में रहती हैं और श्री राज कोलकाता में।"
entities = ner.extract(text, language="hi")

persons   = [e for e in entities if e.entity_type == "PERSON"]
locations = [e for e in entities if e.entity_type == "LOCATION"]

print("Persons:",   [e.text for e in persons])
print("Locations:", [e.text for e in locations])
```

### Pattern 3 — Language metadata lookup

```python
from aumai_bharatvaani.core import SCHEDULED_LANGUAGES

# Look up a language by BCP-47 code
lang = SCHEDULED_LANGUAGES.get("ta")
if lang:
    print(f"{lang.name} is written in the {lang.script} script.")
    print(f"Approximately {lang.speakers_millions:.0f} million speakers.")

# Find all Devanagari-script languages
devanagari_langs = [
    lang for lang in SCHEDULED_LANGUAGES.values()
    if lang.script == "Devanagari"
]
print("Devanagari languages:", [lang.name for lang in devanagari_langs])
```

### Pattern 4 — Bulk transliteration of a word list

```python
from aumai_bharatvaani.core import IndicTransliterator

t = IndicTransliterator()
words = ["नमस्ते", "भारत", "धन्यवाद", "स्वागत"]

romanized = {word: t.to_latin(word, source_script="devanagari") for word in words}
for original, latin in romanized.items():
    print(f"  {original} -> {latin}")
```

### Pattern 5 — Token-level sentiment pipeline

Combine the tokenizer and sentiment analyser to identify which words drive the overall score:

```python
from aumai_bharatvaani.core import IndicTokenizer, IndicSentimentAnalyzer

tokenizer = IndicTokenizer()
analyzer  = IndicSentimentAnalyzer()

text = "यह बहुत अच्छा और खुश करने वाला है।"
tokens = tokenizer.tokenize(text, language="hi")

full_result = analyzer.analyze(text, "hi")
print(f"Full text: {full_result.sentiment} ({full_result.score:+.4f})")

print("Token contributions:")
for token in tokens:
    result = analyzer.analyze(token, language="hi")
    if result.score != 0.0:
        print(f"  '{token}': {result.sentiment} ({result.score:+.4f})")
```

---

## Troubleshooting FAQ

**Q1. I get `ModuleNotFoundError: No module named 'aumai_bharatvaani'` after installing.**

Run `pip show aumai-bharatvaani` to confirm the package is installed in the correct Python
environment. If you use a virtual environment, activate it before running your script:
`source .venv/bin/activate` (Linux/Mac) or `.venv\Scripts\activate` (Windows).

---

**Q2. Which BCP-47 codes are valid?**

Run `aumai-bharatvaani languages` or inspect `SCHEDULED_LANGUAGES.keys()` in Python. Common codes:

| Code | Language | Script |
|------|----------|--------|
| `hi` | Hindi | Devanagari |
| `bn` | Bengali | Bengali |
| `ta` | Tamil | Tamil |
| `te` | Telugu | Telugu |
| `mr` | Marathi | Devanagari |
| `gu` | Gujarati | Gujarati |
| `pa` | Punjabi | Gurmukhi |
| `kn` | Kannada | Kannada |
| `ml` | Malayalam | Malayalam |
| `ur` | Urdu | Perso-Arabic |
| `or` | Odia | Odia |
| `sa` | Sanskrit | Devanagari |

---

**Q3. Sentiment always returns "neutral" for my text. Why?**

Sentiment analysis is lexicon-based. If none of the words in your text appear in the built-in
lexicon for the chosen language, the score will be 0.0 and the label will be "neutral". Lexicons
are currently most complete for `hi`, `bn`, `ta`, and `te`. For other languages you can extend
the lexicon at runtime — see Q8.

---

**Q4. NER finds no entities. What should I check?**

The NER engine matches honorific prefixes (e.g. `श्री`, `डॉ`, `শ্রী`) for persons, and a fixed
list of city/location keywords for locations. If your text does not contain these patterns, no
entities will be returned. Person and location rules are currently populated for `hi`, `bn`, `ta`,
and `te`. Other language codes will produce empty results.

---

**Q5. `to_latin()` raises `ValueError: Script '...' is not supported`.**

Only `"devanagari"` and `"bengali"` are currently valid source scripts. Pass the name in
lowercase exactly as shown. Example:

```python
t.to_latin(text, source_script="devanagari")  # correct
t.to_latin(text, source_script="Devanagari")  # raises ValueError
```

---

**Q6. The romanized output looks approximate. Is this expected?**

Yes. The transliteration tables implement a simplified character-level ISO 15919 / ITRANS mapping.
They handle individual Unicode code points but do not model all conjunct consonant clusters or
context-sensitive rules. For publication-quality romanization, validate the output with a native
speaker.

---

**Q7. Can I add custom words to the sentiment lexicon?**

Yes. The lexicon dictionaries are module-level `dict` objects and can be extended at runtime:

```python
from aumai_bharatvaani import core

# Add custom Hindi words
core._SENTIMENT_LEXICONS["hi"]["उत्कृष्ट"] = 0.95   # "excellent"
core._SENTIMENT_LEXICONS["hi"]["विफल"]     = -0.85   # "fail"
```

This modifies module state globally for the duration of your process. A future release will
expose a cleaner extension API.

---

**Q8. The CLI fails with "Missing option '--language'".**

Both `--text` and `--language` are required for the `tokenize`, `sentiment`, and `ner` commands.
Always supply both:

```bash
aumai-bharatvaani sentiment --text "..." --language hi
```

Use `aumai-bharatvaani <command> --help` to see all required options for any subcommand.
