"""Core logic for aumai-bharatvaani."""

from __future__ import annotations

import re

from aumai_bharatvaani.models import IndicLanguage, NEREntity, SentimentResult

__all__ = [
    "SCHEDULED_LANGUAGES",
    "IndicTokenizer",
    "IndicSentimentAnalyzer",
    "IndicNER",
    "IndicTransliterator",
]

# ---------------------------------------------------------------------------
# 22 Indian Scheduled Languages
# ---------------------------------------------------------------------------

SCHEDULED_LANGUAGES: dict[str, IndicLanguage] = {
    "as": IndicLanguage(code="as", name="Assamese", name_native="অসমীয়া", script="Bengali", speakers_millions=15.0),
    "bn": IndicLanguage(code="bn", name="Bengali", name_native="বাংলা", script="Bengali", speakers_millions=228.0),
    "bo": IndicLanguage(code="bo", name="Bodo", name_native="बर'", script="Devanagari", speakers_millions=1.5),
    "doi": IndicLanguage(code="doi", name="Dogri", name_native="डोगरी", script="Devanagari", speakers_millions=2.6),
    "gu": IndicLanguage(code="gu", name="Gujarati", name_native="ગુજરાતી", script="Gujarati", speakers_millions=56.0),
    "hi": IndicLanguage(code="hi", name="Hindi", name_native="हिन्दी", script="Devanagari", speakers_millions=600.0),
    "kn": IndicLanguage(code="kn", name="Kannada", name_native="ಕನ್ನಡ", script="Kannada", speakers_millions=44.0),
    "ks": IndicLanguage(code="ks", name="Kashmiri", name_native="کشمیری", script="Perso-Arabic", speakers_millions=6.8),
    "kok": IndicLanguage(code="kok", name="Konkani", name_native="कोंकणी", script="Devanagari", speakers_millions=2.3),
    "mai": IndicLanguage(code="mai", name="Maithili", name_native="मैथिली", script="Devanagari", speakers_millions=13.5),
    "ml": IndicLanguage(code="ml", name="Malayalam", name_native="മലയാളം", script="Malayalam", speakers_millions=35.0),
    "mni": IndicLanguage(code="mni", name="Manipuri", name_native="মৈতৈলোন্", script="Bengali", speakers_millions=1.8),
    "mr": IndicLanguage(code="mr", name="Marathi", name_native="मराठी", script="Devanagari", speakers_millions=83.0),
    "ne": IndicLanguage(code="ne", name="Nepali", name_native="नेपाली", script="Devanagari", speakers_millions=16.0),
    "or": IndicLanguage(code="or", name="Odia", name_native="ଓଡ଼ିଆ", script="Odia", speakers_millions=35.0),
    "pa": IndicLanguage(code="pa", name="Punjabi", name_native="ਪੰਜਾਬੀ", script="Gurmukhi", speakers_millions=125.0),
    "sa": IndicLanguage(code="sa", name="Sanskrit", name_native="संस्कृतम्", script="Devanagari", speakers_millions=0.025),
    "sat": IndicLanguage(code="sat", name="Santali", name_native="ᱥᱟᱱᱛᱟᱲᱤ", script="Ol Chiki", speakers_millions=7.6),
    "sd": IndicLanguage(code="sd", name="Sindhi", name_native="سنڌي", script="Perso-Arabic", speakers_millions=25.0),
    "si": IndicLanguage(code="si", name="Sinhala", name_native="සිංහල", script="Sinhala", speakers_millions=16.0),
    "ta": IndicLanguage(code="ta", name="Tamil", name_native="தமிழ்", script="Tamil", speakers_millions=75.0),
    "te": IndicLanguage(code="te", name="Telugu", name_native="తెలుగు", script="Telugu", speakers_millions=82.0),
    "ur": IndicLanguage(code="ur", name="Urdu", name_native="اردو", script="Perso-Arabic", speakers_millions=230.0),
}

# ---------------------------------------------------------------------------
# Sentiment lexicons (word -> polarity score)
# ---------------------------------------------------------------------------

_SENTIMENT_LEXICONS: dict[str, dict[str, float]] = {
    "hi": {
        # Positive
        "अच्छा": 0.8, "बहुत": 0.3, "खुश": 0.9, "प्यार": 0.9, "सुंदर": 0.8,
        "शानदार": 0.9, "बढ़िया": 0.8, "मदद": 0.5, "सफल": 0.8, "स्वास्थ्य": 0.6,
        # Negative
        "बुरा": -0.8, "दुखी": -0.9, "नफरत": -0.9, "गंदा": -0.7, "बीमार": -0.7,
        "परेशान": -0.7, "डर": -0.7, "हिंसा": -0.9, "झूठ": -0.8, "बेकार": -0.8,
    },
    "bn": {
        "ভালো": 0.8, "সুন্দর": 0.8, "খুশি": 0.9, "ভালোবাসা": 0.9, "দারুণ": 0.9,
        "খারাপ": -0.8, "দুঃখ": -0.9, "ঘৃণা": -0.9, "ভয়": -0.7, "বিপদ": -0.8,
    },
    "ta": {
        "நல்ல": 0.8, "அழகான": 0.8, "மகிழ்ச்சி": 0.9, "அன்பு": 0.9,
        "கெட்ட": -0.8, "வலி": -0.7, "வெறுப்பு": -0.9, "பயம்": -0.7,
    },
    "te": {
        "మంచి": 0.8, "అందమైన": 0.8, "సంతోషం": 0.9, "ప్రేమ": 0.9,
        "చెడు": -0.8, "దుఃఖం": -0.9, "ద్వేషం": -0.9, "భయం": -0.7,
    },
}

# ---------------------------------------------------------------------------
# NER patterns (heuristic rule-based)
# ---------------------------------------------------------------------------

# Common Indic honorifics and name prefixes for person detection
_PERSON_PREFIXES: dict[str, list[str]] = {
    "hi": ["श्री", "श्रीमती", "डॉ", "प्रोफेसर", "सर"],
    "bn": ["শ্রী", "শ্রীমতী", "ডাক্তার", "প্রফেসর"],
    "ta": ["திரு", "திருமதி", "டாக்டர்"],
    "te": ["శ్రీ", "శ్రీమతి", "డాక్టర్"],
}

# Common location suffixes for Indic languages
_LOCATION_PATTERNS: dict[str, list[str]] = {
    "hi": ["नगर", "पुर", "गाँव", "शहर", "दिल्ली", "मुंबई", "कोलकाता", "चेन्नई"],
    "bn": ["নগর", "পুর", "শহর", "ঢাকা", "কলকাতা"],
    "ta": ["நகர", "பூர்", "சென்னை", "மும்பை"],
    "te": ["నగర", "పూర్", "హైదరాబాద్"],
}


class IndicTokenizer:
    """Indic-aware tokenizer handling conjuncts and vowel signs."""

    def tokenize(self, text: str, language: str) -> list[str]:
        """Tokenize Indic text.

        Handles Devanagari conjuncts by preserving virama-joined sequences
        as single tokens. Falls back to whitespace splitting for other scripts.

        Args:
            text: Input text in an Indic script.
            language: BCP-47 language code.

        Returns:
            List of string tokens.
        """
        lang_info = SCHEDULED_LANGUAGES.get(language)
        script = lang_info.script if lang_info else "Devanagari"

        if script == "Devanagari":
            return self._tokenize_devanagari(text)
        if script in {"Bengali", "Odia", "Gurmukhi", "Gujarati", "Malayalam",
                      "Kannada", "Telugu", "Tamil"}:
            return self._tokenize_brahmic(text)
        # Generic fallback
        return text.split()

    def _tokenize_devanagari(self, text: str) -> list[str]:
        """Split on whitespace preserving Devanagari word boundaries."""
        # Split on whitespace and punctuation that are not part of Devanagari
        tokens = re.split(r"[\s\u0964\u0965।॥,।!?]+", text.strip())
        return [t for t in tokens if t]

    def _tokenize_brahmic(self, text: str) -> list[str]:
        """Generic Brahmic script tokenizer: whitespace + punctuation split."""
        tokens = re.split(r"[\s,।!?।॥\.\u0964\u0965]+", text.strip())
        return [t for t in tokens if t]


class IndicSentimentAnalyzer:
    """Lexicon-based sentiment analysis for Indic languages."""

    def analyze(self, text: str, language: str) -> SentimentResult:
        """Analyse sentiment of Indic text using a lexicon.

        Args:
            text: The input text.
            language: BCP-47 language code.

        Returns:
            SentimentResult with polarity label and numeric score.
        """
        lexicon = _SENTIMENT_LEXICONS.get(language, {})
        tokenizer = IndicTokenizer()
        tokens = tokenizer.tokenize(text, language)

        scores: list[float] = []
        for token in tokens:
            if token in lexicon:
                scores.append(lexicon[token])

        if not scores:
            return SentimentResult(text=text, language=language, sentiment="neutral", score=0.0)

        aggregate = sum(scores) / len(scores)
        aggregate = max(-1.0, min(1.0, aggregate))

        if aggregate > 0.1:
            label = "positive"
        elif aggregate < -0.1:
            label = "negative"
        else:
            label = "neutral"

        return SentimentResult(text=text, language=language, sentiment=label, score=round(aggregate, 4))


class IndicNER:
    """Rule-based Named Entity Recognition for Indic languages."""

    def extract(self, text: str, language: str) -> list[NEREntity]:
        """Extract named entities from Indic text.

        Uses prefix/suffix heuristics for PERSON, LOCATION, and ORGANIZATION.

        Args:
            text: The input text.
            language: BCP-47 language code.

        Returns:
            List of NEREntity objects.
        """
        entities: list[NEREntity] = []
        entities.extend(self._find_persons(text, language))
        entities.extend(self._find_locations(text, language))
        return entities

    def _find_persons(self, text: str, language: str) -> list[NEREntity]:
        prefixes = _PERSON_PREFIXES.get(language, [])
        entities: list[NEREntity] = []
        for prefix in prefixes:
            pattern = re.escape(prefix) + r"\s+[\w\u0900-\u0D7F]+"
            for match in re.finditer(pattern, text):
                entities.append(NEREntity(
                    text=match.group(),
                    entity_type="PERSON",
                    start=match.start(),
                    end=match.end(),
                    language=language,
                ))
        return entities

    def _find_locations(self, text: str, language: str) -> list[NEREntity]:
        patterns = _LOCATION_PATTERNS.get(language, [])
        entities: list[NEREntity] = []
        for loc_pattern in patterns:
            for match in re.finditer(re.escape(loc_pattern), text):
                entities.append(NEREntity(
                    text=match.group(),
                    entity_type="LOCATION",
                    start=match.start(),
                    end=match.end(),
                    language=language,
                ))
        return entities


# ---------------------------------------------------------------------------
# Devanagari <-> Latin transliteration (ISO 15919 / ITRANS simplified)
# ---------------------------------------------------------------------------

_DEVA_TO_LATIN: dict[str, str] = {
    "अ": "a", "आ": "ā", "इ": "i", "ई": "ī", "उ": "u", "ऊ": "ū",
    "ऋ": "ṛ", "ए": "e", "ऐ": "ai", "ओ": "o", "औ": "au",
    "ा": "ā", "ि": "i", "ी": "ī", "ु": "u", "ू": "ū",
    "ृ": "ṛ", "े": "e", "ै": "ai", "ो": "o", "ौ": "au",
    "क": "k", "ख": "kh", "ग": "g", "घ": "gh", "ङ": "ṅ",
    "च": "c", "छ": "ch", "ज": "j", "झ": "jh", "ञ": "ñ",
    "ट": "ṭ", "ठ": "ṭh", "ड": "ḍ", "ढ": "ḍh", "ण": "ṇ",
    "त": "t", "थ": "th", "द": "d", "ध": "dh", "न": "n",
    "प": "p", "फ": "ph", "ब": "b", "भ": "bh", "म": "m",
    "य": "y", "र": "r", "ल": "l", "व": "v", "श": "ś",
    "ष": "ṣ", "स": "s", "ह": "h",
    "ं": "ṃ", "ः": "ḥ", "्": "", "ँ": "m̐", "ऽ": "'",
    "।": ".", "॥": "..",
}

# Bengali script -> Latin (simplified)
_BENG_TO_LATIN: dict[str, str] = {
    "অ": "a", "আ": "ā", "ই": "i", "ঈ": "ī", "উ": "u", "ঊ": "ū",
    "এ": "e", "ঐ": "ai", "ও": "o", "ঔ": "au",
    "ক": "k", "খ": "kh", "গ": "g", "ঘ": "gh", "ঙ": "ṅ",
    "চ": "c", "ছ": "ch", "জ": "j", "ঝ": "jh", "ঞ": "ñ",
    "ট": "ṭ", "ঠ": "ṭh", "ড": "ḍ", "ঢ": "ḍh", "ণ": "ṇ",
    "ত": "t", "থ": "th", "দ": "d", "ধ": "dh", "ন": "n",
    "প": "p", "ফ": "ph", "ব": "b", "ভ": "bh", "ম": "m",
    "য": "y", "র": "r", "ল": "l", "শ": "ś", "স": "s", "হ": "h",
    "া": "ā", "ি": "i", "ী": "ī", "ু": "u", "ূ": "ū",
    "ে": "e", "ৈ": "ai", "ো": "o", "ৌ": "au",
    "ং": "ṃ", "ঃ": "ḥ", "্": "",
}

_SCRIPT_TO_TABLE: dict[str, dict[str, str]] = {
    "devanagari": _DEVA_TO_LATIN,
    "bengali": _BENG_TO_LATIN,
}


class IndicTransliterator:
    """Transliterate Indic scripts to/from Latin and between Indic scripts."""

    def to_latin(self, text: str, source_script: str) -> str:
        """Transliterate from any supported Indic script to Latin.

        Args:
            text: Source text.
            source_script: Script name (e.g. 'devanagari', 'bengali').

        Returns:
            Romanized string.

        Raises:
            ValueError: If the source script is not supported.
        """
        table = _SCRIPT_TO_TABLE.get(source_script.lower())
        if table is None:
            raise ValueError(
                f"Script '{source_script}' is not supported. "
                f"Supported: {sorted(_SCRIPT_TO_TABLE.keys())}"
            )
        result: list[str] = []
        for char in text:
            result.append(table.get(char, char))
        return "".join(result)

    def between_scripts(self, text: str, source: str, target: str) -> str:
        """Transliterate between two Indic scripts via Latin as pivot.

        Args:
            text: Source text.
            source: Source script name.
            target: Target script name.

        Returns:
            Text in target script (approximation via pivot).

        Raises:
            ValueError: If direct source->target is not supported.
        """
        if target.lower() == "latin":
            return self.to_latin(text, source)

        # For Indic -> Indic we pivot through Latin romanization.
        # In a production system this would use Unicode codepoint mappings.
        # Here we return a best-effort romanized form with a note.
        latin = self.to_latin(text, source)
        return f"[{target}:{latin}]"
