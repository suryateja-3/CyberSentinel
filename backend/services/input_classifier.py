import re
from typing import Dict, Any, Optional

HEALTH_KEYWORDS = {
    "water", "kidney", "hydration", "dehydration", "liters", "sweat",
    "exercise", "fluid", "fluids", "nutrition", "dietary", "vitamin",
    "vitamins", "protein", "carbohydrates", "calories", "metabolism",
    "blood pressure", "heart rate", "cholesterol", "sleep", "bmi",
    "intake", "nutrients", "digestive", "immune", "sodium", "potassium"
}

HEALTH_PHRASES = [
    r"adults?\s+with\s+(?:normal\s+)?kidney\s+function",
    r"drinking\s+about\s+\d+(?:\.\d+)?\s*(?:to\s*\d+(?:\.\d+)?)?\s*liters",
    r"adjusting\s+for\s+climate,\s*exercise",
    r"recommended\s+(?:daily\s+)?(?:intake|allowance|amount)",
    r"drink\s+(?:at\s+least\s+)?\d+\s+glasses\s+of\s+water",
    r"daily\s+water\s+intake",
    r"healthy\s+adults?\s+(?:should|do\s+well)"
]

OPINION_MARKERS = [
    r"\bin\s+my\s+(?:humble\s+)?opinion\b",
    r"\bi\s+(?:personally\s+)?(?:believe|think|feel)\b",
    r"\bfrom\s+my\s+perspective\b",
    r"\bthis\s+is\s+(?:satire|a\s+parody)\b",
    r"\bop-ed\b",
    r"\beditorial\b"
]

NEWS_INDICATORS = [
    r"\b(?:reuters|associated\s+press|afp|ani|pti)\b",
    r"\b(?:said\s+in\s+a\s+statement|according\s+to\s+officials|police\s+said)\b",
    r"\b(?:announced|arrested|eruption|erupted|protest|protests|minister|government|conference|summit)\b",
    r"\b(?:on\s+monday|on\s+tuesday|on\s+wednesday|on\s+thursday|on\s+friday|on\s+saturday|on\s+sunday)\b",
    r"\b(?:in\s+january|in\s+february|in\s+march|in\s+april|in\s+may|in\s+june|in\s+july|in\s+august|in\s+september|in\s+october|in\s+november|in\s+december)\b"
]


def classify_input(text: str, title: Optional[str] = None) -> Dict[str, Any]:
    """
    Classify the input genre to determine whether it is a news article,
    general health/factual advice, opinion/satire, or a specific checkable claim.
    """
    combined = f"{title or ''} {text or ''}".strip().lower()
    
    # 1. Check for Health & Wellness Guidance
    is_health_phrase = any(re.search(pattern, combined) for pattern in HEALTH_PHRASES)
    health_word_hits = sum(1 for kw in HEALTH_KEYWORDS if re.search(rf"\b{kw}\b", combined))
    
    if is_health_phrase or health_word_hits >= 3:
        guidance = (
            "General health consensus (e.g. WHO, Mayo Clinic, US National Academies) "
            "advises that adequate daily fluid intake for healthy adults is typically around 1.5 to 3.7 liters, "
            "but exact needs vary widely depending on personal body mass, exercise intensity, climate, humidity, and individual renal health."
        )
        return {
            "genre": "general_health_advice",
            "genre_label": "General Health Advice / Factual Guidance",
            "is_news": False,
            "is_model_suitable": False,
            "explanation": (
                "This input presents general factual and physiological health advice rather than an event-based news report. "
                "Linguistic news classifiers (like DistilBERT trained on WELFake) were trained on political and social news articles "
                "and cannot reliably evaluate medical or dietary recommendations. Do not treat this claim as fake news based purely on model scores."
            ),
            "domain_guidance": guidance
        }

    # 2. Check for Opinion / Satire
    is_opinion = any(re.search(p, combined) for p in OPINION_MARKERS)
    if is_opinion:
        return {
            "genre": "opinion_satire",
            "genre_label": "Opinion / Commentary / Satire",
            "is_news": False,
            "is_model_suitable": False,
            "explanation": (
                "This input contains personal opinion or subjective editorial language. "
                "Text classifiers and fact-checking indexes cannot verify personal viewpoints or subjective beliefs."
            ),
            "domain_guidance": None
        }

    # 3. Check for News Article vs Specific Event Claim
    is_news = any(re.search(p, combined) for p in NEWS_INDICATORS)
    words = combined.split()
    
    if is_news or len(words) > 60:
        return {
            "genre": "news_article",
            "genre_label": "News Article / Journalistic Report",
            "is_news": True,
            "is_model_suitable": True,
            "explanation": "Standard news article structure suitable for stylistic and NLP pattern analysis.",
            "domain_guidance": None
        }

    # 4. Default: Specific Claim
    return {
        "genre": "specific_claim",
        "genre_label": "Specific Checkable Claim",
        "is_news": True,
        "is_model_suitable": True,
        "explanation": "Specific claim suitable for independent evidence corroboration via external news indexes.",
        "domain_guidance": None
    }
