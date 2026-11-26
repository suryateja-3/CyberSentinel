import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests
from dotenv import load_dotenv

# Ensure .env is loaded if available regardless of working directory
for candidate in (
    Path(__file__).resolve().parents[2] / ".env",
    Path(__file__).resolve().parents[1] / ".env",
    Path(".env").resolve(),
):
    if candidate.exists():
        load_dotenv(dotenv_path=candidate, override=False)
        break

from services.input_classifier import classify_input

GNEWS_API_URL = "https://gnews.io/api/v4/search"


STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "did", "do", "does", "doing", "don't", "down", "during", "each", "few", "for",
    "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers",
    "herself", "him", "himself", "his", "how", "i", "if", "in", "into", "is",
    "isn't", "it", "its", "itself", "just", "me", "more", "most", "my", "myself",
    "no", "nor", "not", "now", "of", "off", "on", "once", "only", "or", "other",
    "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "she",
    "should", "so", "some", "such", "than", "that", "the", "their", "theirs",
    "them", "themselves", "then", "there", "these", "they", "this", "those",
    "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we",
    "were", "weren't", "what", "when", "where", "which", "while", "who", "whom",
    "why", "with", "won't", "would", "you", "your", "yours", "yourself", "yourselves",
    # Noise/clickbait terms
    "exclusive", "breaking", "shocking", "urgent", "unbelievable", "video", "watch",
    "photo", "update", "revealed", "reveals", "share", "deleted", "alert"
}

CONTRADICT_TERMS = [
    "hoax", "false", "debunked", "debunk", "fake", "denies", "misleading",
    "untrue", "fabricated", "disproven", "fact check", "fact-check", "refutes",
    "myth", "no evidence", "bogus", "conspiracy theory", "incorrect", "denied"
]

SUPPORT_TERMS = [
    "confirms", "confirmed", "discovered", "proven", "proves", "agrees",
    "reports", "reported", "announces", "announced", "finds", "found",
    "validates", "shows", "unveils", "launches", "launched", "study finds",
    "published", "official", "statement", "investigation", "probe", "probes",
    "police", "protests", "protest", "unrest", "clashes", "arrested", "arrests",
    "suspended", "postponed", "vandalism", "incident", "stir", "lockdown",
    "arson", "erupted", "demonstrations"
]


def extract_search_terms(text: str, title: Optional[str] = None, max_terms: int = 4) -> str:
    """
    Extract high-signal search terms from a headline and/or article body.
    Prioritizes named entities, acronyms, and key event descriptors.
    """
    source_text = title.strip() if title and title.strip() else text.strip()
    first_sentence = re.split(r'[.!?\n]', source_text)[0].strip()
    if not first_sentence:
        first_sentence = source_text[:200]

    # 1. Look for multi-word proper nouns (e.g. "Lovely Professional University")
    entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', source_text)
    meaningful_entities = [e for e in entities if not any(w.lower() in STOPWORDS for w in e.split())]

    # 2. Look for acronyms (e.g. "NASA", "WHO", "LPU", "EU")
    acronyms = re.findall(r'\b[A-Z]{2,}\b', source_text)

    # 3. Look for key event/action nouns
    event_keywords = [
        w for w in re.findall(r'[a-zA-Z]+', source_text)
        if w.lower() in {
            "protests", "protest", "unrest", "vandalism", "clashes", "arrest", "incident", "strike",
            "fire", "arson", "flood", "earthquake", "election", "water", "ice", "study", "research"
        }
    ]

    if meaningful_entities:
        primary_entity = meaningful_entities[0]
        if event_keywords:
            return f"{primary_entity} {event_keywords[0]}"
        return primary_entity

    if acronyms:
        primary_acronym = acronyms[0]
        if event_keywords:
            return f"{primary_acronym} {event_keywords[0]}"

    # Fallback: clean words in first sentence and filter stopwords
    words = re.findall(r'[a-zA-Z0-9]+', first_sentence)
    meaningful = []
    seen = set()
    for w in words:
        w_lower = w.lower()
        if w_lower not in STOPWORDS and len(w_lower) > 2 and w_lower not in seen:
            meaningful.append(w)
            seen.add(w_lower)

    if not meaningful:
        fallback_words = re.findall(r'[a-zA-Z0-9]+', text)
        for w in fallback_words:
            w_lower = w.lower()
            if w_lower not in STOPWORDS and len(w_lower) > 2 and w_lower not in seen:
                meaningful.append(w)
                seen.add(w_lower)
            if len(meaningful) >= max_terms:
                break

    return " ".join(meaningful[:max_terms])


def verify_claim(claim_text: str, title: Optional[str] = None) -> Dict[str, Any]:
    """
    Search for related coverage using the GNews API, extract real article metadata,
    and evaluate evidence without fabricating claims or asserting absolute truth.
    Reports clear states: SUPPORTED, CONTRADICTED, MIXED EVIDENCE, UNVERIFIED.
    """
    input_classification = classify_input(claim_text, title=title)
    
    api_key = os.environ.get("GNEWS_API_KEY")
    if not api_key:
        return {
            "status": "error",
            "message": "Verification unavailable: API key not configured.",
            "evidence": [],
            "supporting_evidence": [],
            "contradicting_evidence": [],
            "neutral_evidence": [],
            "verdict": "UNVERIFIED",
            "verdict_label": "UNVERIFIED (API Not Configured)",
            "input_classification": input_classification,
            "limitations": "Evidence search requires a configured GNews API key."
        }

    combined_input = f"{title or ''} {claim_text or ''}".strip()
    if not combined_input:
        return {
            "status": "error",
            "message": "Empty claim text.",
            "evidence": [],
            "supporting_evidence": [],
            "contradicting_evidence": [],
            "neutral_evidence": [],
            "verdict": "UNVERIFIED",
            "verdict_label": "UNVERIFIED",
            "input_classification": input_classification
        }

    query = extract_search_terms(claim_text, title=title, max_terms=4)
    if not query:
        return {
            "status": "error",
            "message": "Could not extract searchable terms from claim.",
            "evidence": [],
            "supporting_evidence": [],
            "contradicting_evidence": [],
            "neutral_evidence": [],
            "verdict": "UNVERIFIED",
            "verdict_label": "UNVERIFIED",
            "input_classification": input_classification
        }

    params = {
        "q": query,
        "lang": "en",
        "apikey": api_key,
        "max": 8
    }

    try:
        response = requests.get(GNEWS_API_URL, params=params, timeout=10)
        
        if response.status_code == 429:
            return {
                "status": "error",
                "message": "Verification unavailable: Rate limit exceeded.",
                "evidence": [],
                "supporting_evidence": [],
                "contradicting_evidence": [],
                "neutral_evidence": [],
                "verdict": "UNVERIFIED",
                "verdict_label": "UNVERIFIED (Rate Limit Exceeded)",
                "input_classification": input_classification,
                "explanation": "External news API quota exceeded. A failed API search does NOT mean the claim is false."
            }
        elif response.status_code in (401, 403):
            return {
                "status": "error",
                "message": "Verification unavailable: Authentication or permission problem (Invalid API Key).",
                "evidence": [],
                "supporting_evidence": [],
                "contradicting_evidence": [],
                "neutral_evidence": [],
                "verdict": "UNVERIFIED",
                "verdict_label": "UNVERIFIED (Auth Error)",
                "input_classification": input_classification,
                "explanation": "External news API authentication failed. A failed API search does NOT mean the claim is false."
            }
        
        response.raise_for_status()
        data = response.json()

    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "message": "Verification unavailable: Request timed out.",
            "evidence": [],
            "supporting_evidence": [],
            "contradicting_evidence": [],
            "neutral_evidence": [],
            "verdict": "UNVERIFIED",
            "verdict_label": "UNVERIFIED (Timeout)",
            "input_classification": input_classification,
            "explanation": "The external search request timed out. A failed search does NOT mean the claim is false."
        }
    except requests.exceptions.RequestException as e:
        status_code = e.response.status_code if e.response is not None else "N/A"
        if status_code in (401, 403):
            err_msg = "Verification unavailable: Authentication or permission problem (Invalid API Key)."
        elif status_code == 429:
            err_msg = "Verification unavailable: Rate limit exceeded."
        else:
            err_msg = f"Verification unavailable: API request failed (Status {status_code})."
        return {
            "status": "error",
            "message": err_msg,
            "evidence": [],
            "supporting_evidence": [],
            "contradicting_evidence": [],
            "neutral_evidence": [],
            "verdict": "UNVERIFIED",
            "verdict_label": "UNVERIFIED (API Error)",
            "input_classification": input_classification,
            "explanation": f"API request error occurred (Status {status_code}). A failed API request is never proof that a claim is false."
        }

    # Inspect subscription freshness
    is_free_plan = False
    info_block = data.get("information", {})
    if isinstance(info_block, dict):
        rt_info = info_block.get("realTimeArticles", {})
        if isinstance(rt_info, dict) and "12-hour delay" in rt_info.get("message", ""):
            is_free_plan = True

    freshness_label = "12-hour delay (GNews Free Plan)" if is_free_plan else "Real-time index"
    freshness_notice = (
        "Articles retrieved via GNews Free tier reflect a ~12-hour delay. Breaking events that occurred in the last 12 hours may not yet appear."
        if is_free_plan else
        "Live news feed indexed directly from publisher feeds."
    )

    raw_articles = data.get("articles", [])
    if not raw_articles:
        base_explanation = (
            "No matching news articles were found for the extracted keywords. "
            "This does NOT prove the claim is false; the event may be recent, localized, or unindexed by news feeds."
        )
        if input_classification.get("genre") == "general_health_advice":
            base_explanation = (
                "No breaking news articles found. Note: This text is general health advice rather than news. "
                "News indexes monitor current events and breaking reports, not general medical or physiological guidelines. "
                f"{input_classification.get('domain_guidance') or ''}"
            )

        return {
            "status": "success",
            "message": "No related news reports found.",
            "claim_extracted": query,
            "evidence": [],
            "supporting_evidence": [],
            "contradicting_evidence": [],
            "neutral_evidence": [],
            "verdict": "UNVERIFIED",
            "verdict_label": "UNVERIFIED / INSUFFICIENT EVIDENCE",
            "total_sources": 0,
            "input_classification": input_classification,
            "domain_guidance": input_classification.get("domain_guidance"),
            "provider_info": {
                "provider": "GNews Search API",
                "freshness": freshness_label,
                "freshness_notice": freshness_notice
            },
            "explanation": base_explanation,
            "limitations": "Evidence retrieval depends on search engine coverage and publishing lag. The absence of search results is not proof of falsehood."
        }

    # Process and normalize articles
    all_evidence = []
    supporting = []
    contradicting = []
    neutral = []

    for art in raw_articles:
        source_obj = art.get("source") or {}
        source_name = source_obj.get("name") if isinstance(source_obj, dict) else "News Outlet"
        source_url = source_obj.get("url") if isinstance(source_obj, dict) else ""

        title_text = str(art.get("title") or "").strip()
        desc_text = str(art.get("description") or "").strip()
        pub_date = str(art.get("publishedAt") or "").strip()
        art_url = str(art.get("url") or "").strip()

        combined_item = f"{title_text} {desc_text}".lower()

        is_contradicting = any(term in combined_item for term in CONTRADICT_TERMS)
        is_supporting = (not is_contradicting) and any(term in combined_item for term in SUPPORT_TERMS)

        item = {
            "title": title_text,
            "url": art_url,
            "date": pub_date,
            "source": source_name,
            "source_url": source_url,
            "excerpt": desc_text,
            "category": "contradicting" if is_contradicting else ("supporting" if is_supporting else "neutral")
        }
        all_evidence.append(item)

        if is_contradicting:
            contradicting.append(item)
        elif is_supporting:
            supporting.append(item)
        else:
            neutral.append(item)

    # Determine verdict using clear states: SUPPORTED, CONTRADICTED, MIXED EVIDENCE, UNVERIFIED
    if len(contradicting) > 0 and len(supporting) == 0:
        verdict = "CONTRADICTED"
        verdict_label = "CONTRADICTED"
        explanation = f"Found {len(contradicting)} source(s) with debunking or disputing language (e.g., 'debunked', 'false', 'hoax') regarding this claim."
    elif len(supporting) > 0 and len(contradicting) == 0:
        verdict = "SUPPORTED"
        verdict_label = "SUPPORTED"
        explanation = f"Found {len(supporting)} independent source(s) reporting or corroborating these events without debunking language."
    elif len(supporting) > 0 and len(contradicting) > 0:
        verdict = "MIXED EVIDENCE"
        verdict_label = "MIXED EVIDENCE"
        explanation = f"Retrieved sources show conflicting coverage ({len(supporting)} corroborating vs {len(contradicting)} disputing or fact-checking)."
    else:
        # Related articles found without explicit support or debunking markers
        verdict = "UNVERIFIED"
        verdict_label = "UNVERIFIED / INSUFFICIENT EVIDENCE"
        explanation = f"Found {len(neutral)} related report(s), but none contain explicit corroboration or debunking language. Review source links directly."

    return {
        "status": "success",
        "message": f"Found {len(all_evidence)} related report(s).",
        "claim_extracted": query,
        "verdict": verdict,
        "verdict_label": verdict_label,
        "total_sources": len(all_evidence),
        "supporting_count": len(supporting),
        "contradicting_count": len(contradicting),
        "neutral_count": len(neutral),
        "evidence": all_evidence,
        "supporting_evidence": supporting,
        "contradicting_evidence": contradicting,
        "neutral_evidence": neutral,
        "input_classification": input_classification,
        "domain_guidance": input_classification.get("domain_guidance"),
        "provider_info": {
            "provider": "GNews Search API",
            "freshness": freshness_label,
            "freshness_notice": freshness_notice
        },
        "explanation": explanation,
        "limitations": "Evidence search relies on external news indexes. Lack of matching articles does not prove falsehood, nor does presence of matching keywords guarantee truth. Critical thinking and review of primary sources are required."
    }
