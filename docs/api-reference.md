# API Reference — AumAI BharatVaani

This document covers every public class, function, constant, and Pydantic model exported by
`aumai-bharatvaani`. All symbols listed here are importable from the submodules shown.

---

## Table of Contents

- [Module: `aumai_bharatvaani.models`](#module-aumai_bharatvaanimodels)
  - [IndicLanguage](#indiclanguage)
  - [SentimentResult](#sentimentresult)
  - [NEREntity](#nerentity)
- [Module: `aumai_bharatvaani.core`](#module-aumai_bharatvaanicore)
  - [SCHEDULED_LANGUAGES](#scheduled_languages)
  - [IndicTokenizer](#indictokenizer)
  - [IndicSentimentAnalyzer](#indicsentimentanalyzer)
  - [IndicNER](#indicner)
  - [IndicTransliterator](#indictransliterator)
- [Module: `aumai_bharatvaani.cli`](#module-aumai_bharatvaancli)
  - [CLI Commands](#cli-commands)

---

## Module: `aumai_bharatvaani.models`

Pydantic v2 models that represent the structured data produced by the library.

```python
from aumai_bharatvaani.models import IndicLanguage, SentimentResult, NEREntity
```

---

### `IndicLanguage`

Metadata record for one of the 22 Indian scheduled languages.

```python
class IndicLanguage(BaseModel):
    code: str
    name: str
    name_native: str
    script: str
    speakers_millions: float
```

**Fields**

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `code` | `str` | — | BCP-47 language code, e.g. `"hi"` for Hindi. |
| `name` | `str` | — | English name of the language. |
| `name_native` | `str` | — | Name in the language's own script. |
| `script` | `str` | — | Script family name, e.g. `"Devanagari"`, `"Bengali"`. |
| `speakers_millions` | `float` | `>= 0.0` | Approximate number of speakers in millions. |

**Example**

```python
from aumai_bharatvaani.core import SCHEDULED_LANGUAGES

lang = SCHEDULED_LANGUAGES["hi"]
print(lang.code)              # "hi"
print(lang.name)              # "Hindi"
print(lang.name_native)       # "हिन्दी"
print(lang.script)            # "Devanagari"
print(lang.speakers_millions) # 600.0
```

---

### `SentimentResult`

Result of a sentiment analysis operation on a single text input.

```python
class SentimentResult(BaseModel):
    text: str
    language: str
    sentiment: Literal["positive", "negative", "neutral"]
    score: float
```

**Fields**

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `text` | `str` | — | The original input text that was analysed. |
| `language` | `str` | — | BCP-47 language code used for analysis. |
| `sentiment` | `Literal["positive", "negative", "neutral"]` | — | Human-readable polarity label. |
| `score` | `float` | `-1.0 <= score <= 1.0` | Aggregate sentiment score. Positive values indicate positive sentiment; negative values indicate negative sentiment. |

**Polarity thresholds**

The polarity label is derived from the score as follows:

| Score range | Label |
|-------------|-------|
| `score > 0.1` | `"positive"` |
| `score < -0.1` | `"negative"` |
| `-0.1 <= score <= 0.1` | `"neutral"` |

**Example**

```python
from aumai_bharatvaani.core import IndicSentimentAnalyzer

analyzer = IndicSentimentAnalyzer()
result = analyzer.analyze("यह बहुत अच्छा है।", language="hi")

print(result.sentiment)  # "positive"
print(result.score)      # 0.55
```

---

### `NEREntity`

A single named entity extracted from Indic text.

```python
class NEREntity(BaseModel):
    text: str
    entity_type: str
    start: int
    end: int
    language: str
```

**Fields**

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `text` | `str` | — | The surface form of the entity as it appears in the source text. |
| `entity_type` | `str` | — | Entity category: `"PERSON"`, `"LOCATION"`, or `"ORGANIZATION"`. |
| `start` | `int` | `>= 0` | Character offset (inclusive) of the entity in the source string. |
| `end` | `int` | `>= 0` | Character offset (exclusive) of the entity in the source string. |
| `language` | `str` | — | BCP-47 language code of the source text. |

**Example**

```python
from aumai_bharatvaani.core import IndicNER

ner = IndicNER()
entities = ner.extract("श्री राज दिल्ली में हैं।", language="hi")

for entity in entities:
    print(entity.text, entity.entity_type, entity.start, entity.end)
# श्री राज  PERSON    0  9
# दिल्ली    LOCATION  10 16
```

---

## Module: `aumai_bharatvaani.core`

The primary logic module. Exposes one constant and four classes.

```python
from aumai_bharatvaani.core import (
    SCHEDULED_LANGUAGES,
    IndicTokenizer,
    IndicSentimentAnalyzer,
    IndicNER,
    IndicTransliterator,
)
```

---

### `SCHEDULED_LANGUAGES`

```python
SCHEDULED_LANGUAGES: dict[str, IndicLanguage]
```

A module-level dictionary mapping BCP-47 codes to `IndicLanguage` metadata objects for all 22
Indian scheduled languages.

**Supported codes**

`as`, `bn`, `bo`, `doi`, `gu`, `hi`, `kn`, `ks`, `kok`, `mai`, `ml`, `mni`, `mr`, `ne`, `or`,
`pa`, `sa`, `sat`, `sd`, `ta`, `te`, `ur`

**Example**

```python
from aumai_bharatvaani.core import SCHEDULED_LANGUAGES

# Check if a code is supported
if "ml" in SCHEDULED_LANGUAGES:
    print("Malayalam is supported")

# Iterate all languages
for code, lang in sorted(SCHEDULED_LANGUAGES.items()):
    print(f"{code}: {lang.name}")
```

---

### `IndicTokenizer`

```python
class IndicTokenizer:
    def tokenize(self, text: str, language: str) -> list[str]: ...
```

Indic-aware tokenizer that preserves script-specific word boundaries.

**How it works**

- For **Devanagari** scripts (`hi`, `mr`, `sa`, `ne`, `bo`, `doi`, `kok`, `mai`): splits on
  whitespace and the Devanagari danda/double-danda characters (`।` U+0964, `॥` U+0965) and common
  punctuation.
- For **other Brahmic scripts** (Bengali, Odia, Gurmukhi, Gujarati, Malayalam, Kannada, Telugu,
  Tamil): uses a similar whitespace-and-punctuation split.
- For **all other scripts** (Perso-Arabic, Ol Chiki): falls back to `str.split()`.

#### `IndicTokenizer.tokenize()`

```python
def tokenize(self, text: str, language: str) -> list[str]:
```

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | `str` | Input text in an Indic script. |
| `language` | `str` | BCP-47 language code used to determine the script family. |

**Returns**

`list[str]` — List of string tokens. Empty strings are filtered out.

**Example**

```python
from aumai_bharatvaani.core import IndicTokenizer

t = IndicTokenizer()

# Devanagari (Hindi)
print(t.tokenize("नमस्ते भारत।", "hi"))
# ['नमस्ते', 'भारत']

# Brahmic (Tamil)
print(t.tokenize("வணக்கம் நண்பர்.", "ta"))
# ['வணக்கம்', 'நண்பர்']

# Unknown/fallback
print(t.tokenize("Hello world", "xx"))
# ['Hello', 'world']
```

---

### `IndicSentimentAnalyzer`

```python
class IndicSentimentAnalyzer:
    def analyze(self, text: str, language: str) -> SentimentResult: ...
```

Lexicon-based sentiment analysis for Indic languages. Uses a built-in word-level polarity
dictionary for each supported language. The aggregate score is the mean of all matched token
scores, clamped to [-1.0, 1.0].

**Lexicon coverage**

Built-in lexicons exist for: `hi` (Hindi), `bn` (Bengali), `ta` (Tamil), `te` (Telugu).
Other language codes will always return `sentiment="neutral"` and `score=0.0`.

#### `IndicSentimentAnalyzer.analyze()`

```python
def analyze(self, text: str, language: str) -> SentimentResult:
```

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | `str` | Input text to analyse. |
| `language` | `str` | BCP-47 language code. |

**Returns**

`SentimentResult` — Pydantic model with `text`, `language`, `sentiment`, and `score` fields.

**Notes**

- Tokenizes text with `IndicTokenizer` before looking up tokens in the lexicon.
- Tokens not found in the lexicon are silently ignored.
- If no tokens match the lexicon, returns `sentiment="neutral"` and `score=0.0`.
- The score is rounded to 4 decimal places.

**Example**

```python
from aumai_bharatvaani.core import IndicSentimentAnalyzer

analyzer = IndicSentimentAnalyzer()

# Positive Hindi text
r = analyzer.analyze("यह बहुत अच्छा और शानदार है।", "hi")
print(r.sentiment, r.score)  # positive  0.85

# Negative Hindi text
r = analyzer.analyze("यह बहुत बुरा और बेकार है।", "hi")
print(r.sentiment, r.score)  # negative  -0.8

# Language without lexicon
r = analyzer.analyze("Bonjour monde", "fr")
print(r.sentiment, r.score)  # neutral   0.0
```

---

### `IndicNER`

```python
class IndicNER:
    def extract(self, text: str, language: str) -> list[NEREntity]: ...
```

Rule-based Named Entity Recognition for Indic languages. Uses two types of heuristics:

- **Person detection**: looks for common Indic honorifics and name prefixes followed by a word.
- **Location detection**: matches known city names and location suffixes.

**Language support**

Person and location rules are populated for: `hi`, `bn`, `ta`, `te`.
Other languages return an empty list.

#### `IndicNER.extract()`

```python
def extract(self, text: str, language: str) -> list[NEREntity]:
```

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | `str` | Source text to search for named entities. |
| `language` | `str` | BCP-47 language code. |

**Returns**

`list[NEREntity]` — List of extracted entities. May be empty. Entities from person detection
and location detection are concatenated; the list is not deduplicated or sorted.

**Entity types returned**

| `entity_type` | Detection method |
|---------------|-----------------|
| `"PERSON"` | Honorific prefix regex (e.g. `श्री`, `डॉ`, `শ্রী`, `திரு`) |
| `"LOCATION"` | Known location keyword match (e.g. `दिल्ली`, `মুম্বই`, `சென்னை`) |

**Example**

```python
from aumai_bharatvaani.core import IndicNER

ner = IndicNER()

entities = ner.extract(
    "डॉ प्रिया मुंबई से हैं और श्री राज दिल्ली में।",
    language="hi",
)
for e in entities:
    print(f"[{e.entity_type}] '{e.text}' at ({e.start},{e.end})")
```

---

### `IndicTransliterator`

```python
class IndicTransliterator:
    def to_latin(self, text: str, source_script: str) -> str: ...
    def between_scripts(self, text: str, source: str, target: str) -> str: ...
```

Transliterates Indic scripts to Latin or between Indic scripts. Uses a character-level lookup
table implementing an ISO 15919 / ITRANS approximation.

**Supported source scripts**

| Script name (lowercase) | Languages |
|-------------------------|-----------|
| `"devanagari"` | Hindi, Marathi, Sanskrit, Nepali, Bodo, Dogri, Konkani, Maithili |
| `"bengali"` | Bengali, Assamese, Manipuri |

#### `IndicTransliterator.to_latin()`

```python
def to_latin(self, text: str, source_script: str) -> str:
```

Transliterate from a supported Indic script to Latin romanization.

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | `str` | Source text in an Indic script. |
| `source_script` | `str` | Script name in lowercase: `"devanagari"` or `"bengali"`. |

**Returns**

`str` — Romanized string. Characters not found in the lookup table are passed through unchanged.

**Raises**

| Exception | Condition |
|-----------|-----------|
| `ValueError` | `source_script` is not in the supported set. The error message lists valid options. |

**Example**

```python
from aumai_bharatvaani.core import IndicTransliterator

t = IndicTransliterator()

print(t.to_latin("नमस्ते", "devanagari"))  # "namaste"
print(t.to_latin("বাংলা",  "bengali"))     # "bāṃlā"

try:
    t.to_latin("hello", "tamil")
except ValueError as exc:
    print(exc)
# Script 'tamil' is not supported. Supported: ['bengali', 'devanagari']
```

#### `IndicTransliterator.between_scripts()`

```python
def between_scripts(self, text: str, source: str, target: str) -> str:
```

Transliterate between two scripts. When `target` is `"latin"` this delegates to `to_latin()`.
For all other targets, the method pivots through a Latin romanization and returns the result
in a bracketed notation `[target:latinized]`. Direct Indic-to-Indic script conversion requires
full Unicode codepoint mapping tables which are planned for a future release.

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | `str` | Source text. |
| `source` | `str` | Source script name (lowercase). |
| `target` | `str` | Target script name (lowercase), e.g. `"latin"`, `"bengali"`. |

**Returns**

`str` — Romanized text when `target="latin"`. For other targets, returns `"[target:latin_pivot]"`.

**Raises**

| Exception | Condition |
|-----------|-----------|
| `ValueError` | `source` script is not supported (propagated from `to_latin()`). |

**Example**

```python
t = IndicTransliterator()

# Devanagari to Latin
print(t.between_scripts("नमस्ते", source="devanagari", target="latin"))
# "namaste"

# Devanagari to Bengali (pivot notation)
print(t.between_scripts("नमस्ते", source="devanagari", target="bengali"))
# "[bengali:namaste]"
```

---

## Module: `aumai_bharatvaani.cli`

Command-line interface entry point. Installed as the `aumai-bharatvaani` executable.

```bash
aumai-bharatvaani --help
aumai-bharatvaani --version
```

---

### CLI Commands

All commands accept `--help` for full option documentation.

#### `languages`

List all 22 Indian scheduled languages with their codes, native names, scripts, and speaker counts.

```bash
aumai-bharatvaani languages
```

**Output format** (space-padded columns):

```
code   English name         Native name              script=<script>  speakers=<N>M
```

---

#### `tokenize`

Tokenize a text string and print the resulting tokens separated by ` | `.

```bash
aumai-bharatvaani tokenize --text TEXT --language LANG
```

| Option | Required | Description |
|--------|----------|-------------|
| `--text` | Yes | Input text string. |
| `--language` | Yes | BCP-47 language code (e.g. `hi`, `ta`, `bn`). |

**Example**

```bash
aumai-bharatvaani tokenize --text "नमस्ते भारत।" --language hi
# Tokens (2): नमस्ते | भारत
```

---

#### `sentiment`

Analyse the sentiment of a text string and print the label and score.

```bash
aumai-bharatvaani sentiment --text TEXT --language LANG
```

| Option | Required | Description |
|--------|----------|-------------|
| `--text` | Yes | Input text string. |
| `--language` | Yes | BCP-47 language code. |

**Example**

```bash
aumai-bharatvaani sentiment --text "यह बहुत अच्छा है" --language hi
# Sentiment: POSITIVE
# Score:     +0.5500
```

---

#### `ner`

Extract named entities from a text string and print them.

```bash
aumai-bharatvaani ner --text TEXT --language LANG
```

| Option | Required | Description |
|--------|----------|-------------|
| `--text` | Yes | Input text string. |
| `--language` | Yes | BCP-47 language code. |

**Example**

```bash
aumai-bharatvaani ner --text "श्री राज दिल्ली में हैं।" --language hi
# [PERSON]   'श्री राज'   span=(0,9)
# [LOCATION] 'दिल्ली'     span=(10,16)
```

If no entities are found, prints: `No named entities found.`

---

#### `transliterate`

Transliterate text from one script to another.

```bash
aumai-bharatvaani transliterate --text TEXT --from SOURCE --to TARGET
```

| Option | Required | Description |
|--------|----------|-------------|
| `--text` | Yes | Input text string. |
| `--from` | Yes | Source script name (e.g. `devanagari`, `bengali`). |
| `--to` | Yes | Target script name (e.g. `latin`). |

**Example**

```bash
aumai-bharatvaani transliterate --text "नमस्ते" --from devanagari --to latin
# namaste
```

Exits with code `1` and prints an error to stderr if the source script is unsupported.
