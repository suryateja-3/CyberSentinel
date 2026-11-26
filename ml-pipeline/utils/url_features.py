"""
utils/url_features.py
=====================
Lexical feature extractor for URL classification.

Extracts 22 hand-crafted, interpretable features from a raw URL string.
These features are used as input to the Random Forest classifier.

IMPORTANT: This extractor uses ONLY the URL string — no DNS lookups,
no HTTP requests, no WHOIS queries.  This avoids data leakage and keeps
inference fast and offline, but means the model cannot detect threats
that require live network information.
"""

from __future__ import annotations

import re
import string
from typing import List
from urllib.parse import urlparse

import numpy as np


# ---------------------------------------------------------------------------
# Feature definitions (22 features)
# ---------------------------------------------------------------------------

FEATURE_NAMES: List[str] = [
    "url_length",              # 0  Total character count of the full URL
    "hostname_length",         # 1  Length of the hostname part
    "path_length",             # 2  Length of the path component
    "query_length",            # 3  Length of the query string
    "num_dots",                # 4  Total dot characters in URL
    "num_hyphens",             # 5  Total hyphen characters in URL
    "num_underscores",         # 6  Total underscore characters
    "num_slashes",             # 7  Total forward slashes
    "num_digits",              # 8  Total digit characters
    "num_special_chars",       # 9  @, !, $, %, ^, &, *, (, )
    "num_subdomains",          # 10 Number of subdomain levels (dots in host − 1)
    "has_ip_address",          # 11 1 if hostname is an IP address, else 0
    "has_https",               # 12 1 if scheme is https, else 0
    "has_suspicious_words",    # 13 1 if URL contains phishing-related keywords
    "has_at_symbol",           # 14 1 if '@' present in URL (classic phishing trick)
    "has_double_slash_redirect",# 15 1 if '//' appears in path (redirect indicator)
    "tld_in_subdomain",        # 16 1 if TLD-like string found in subdomain
    "is_shortened_url",        # 17 1 if known URL shortener domain
    "entropy",                 # 18 Shannon entropy of URL characters
    "digit_ratio",             # 19 Fraction of characters that are digits
    "uppercase_ratio",         # 20 Fraction of characters that are uppercase
    "path_depth",              # 21 Number of segments in the URL path
]

_SUSPICIOUS_WORDS = frozenset([
    "login", "signin", "verify", "update", "secure", "account", "banking",
    "paypal", "ebay", "amazon", "google", "microsoft", "apple", "confirm",
    "password", "credential", "wallet", "invoice", "support", "free",
    "lucky", "winner", "prize", "click", "urgent", "alert", "suspend",
    "unusual", "activity", "validate", "restore", "unlock",
])

_URL_SHORTENERS = frozenset([
    "bit.ly", "tinyurl.com", "goo.gl", "ow.ly", "t.co", "is.gd",
    "buff.ly", "adf.ly", "rb.gy", "cutt.ly", "shorturl.at", "tiny.cc",
    "lnkd.in", "mcaf.ee", "s.id",
])

_IP_RE = re.compile(
    r"^(\d{1,3}\.){3}\d{1,3}$"
)

_TLD_LIKE = re.compile(
    r"\.(com|net|org|gov|edu|info|io|co)\."
)


def _shannon_entropy(s: str) -> float:
    """Compute the Shannon entropy (in bits) of a string."""
    if not s:
        return 0.0
    freq = np.bincount(np.frombuffer(s.encode("utf-8", errors="replace"), dtype=np.uint8), minlength=256)
    prob = freq / freq.sum()
    prob = prob[prob > 0]
    return float(-np.sum(prob * np.log2(prob)))


# ---------------------------------------------------------------------------
# Main extraction function
# ---------------------------------------------------------------------------

def extract_features(url: str) -> List[float]:
    """
    Extract 22 lexical features from a single URL string.

    Parameters
    ----------
    url : str
        The raw URL to analyse (including scheme if present).

    Returns
    -------
    list[float]
        A list of 22 numeric features in the order defined by FEATURE_NAMES.
    """
    url = str(url).strip()

    # Ensure parseable
    if not url.startswith(("http://", "https://", "ftp://")):
        url_to_parse = "http://" + url
    else:
        url_to_parse = url

    try:
        parsed = urlparse(url_to_parse)
    except Exception:
        parsed = urlparse("http://unknown")

    hostname  = parsed.hostname or ""
    path      = parsed.path or ""
    query     = parsed.query or ""
    url_lower = url.lower()

    # 0 – URL length
    feat_url_length = len(url)

    # 1 – Hostname length
    feat_hostname_length = len(hostname)

    # 2 – Path length
    feat_path_length = len(path)

    # 3 – Query length
    feat_query_length = len(query)

    # 4 – Number of dots
    feat_num_dots = url.count(".")

    # 5 – Number of hyphens
    feat_num_hyphens = url.count("-")

    # 6 – Number of underscores
    feat_num_underscores = url.count("_")

    # 7 – Number of slashes
    feat_num_slashes = url.count("/")

    # 8 – Number of digits
    feat_num_digits = sum(c.isdigit() for c in url)

    # 9 – Special characters
    _special = set("@!$%^&*()")
    feat_num_special = sum(c in _special for c in url)

    # 10 – Number of subdomains
    parts = hostname.split(".")
    feat_num_subdomains = max(len(parts) - 2, 0)

    # 11 – Has IP address as hostname
    feat_has_ip = int(bool(_IP_RE.match(hostname)))

    # 12 – Has HTTPS
    feat_has_https = int(parsed.scheme == "https")

    # 13 – Suspicious words
    feat_suspicious = int(any(w in url_lower for w in _SUSPICIOUS_WORDS))

    # 14 – Has @ symbol
    feat_has_at = int("@" in url)

    # 15 – Double-slash redirect in path
    feat_double_slash = int("//" in path)

    # 16 – TLD-like string in subdomain portion
    subdomain_part = ".".join(parts[:-2]) if len(parts) > 2 else ""
    feat_tld_subdomain = int(bool(_TLD_LIKE.search("." + subdomain_part + ".")))

    # 17 – Known URL shortener
    feat_shortened = int(hostname.lower() in _URL_SHORTENERS)

    # 18 – Shannon entropy
    feat_entropy = _shannon_entropy(url)

    # 19 – Digit ratio
    feat_digit_ratio = feat_num_digits / max(len(url), 1)

    # 20 – Uppercase ratio
    feat_upper_ratio = sum(c.isupper() for c in url) / max(len(url), 1)

    # 21 – Path depth (number of '/' separated segments)
    feat_path_depth = len([p for p in path.split("/") if p])

    return [
        feat_url_length,
        feat_hostname_length,
        feat_path_length,
        feat_query_length,
        feat_num_dots,
        feat_num_hyphens,
        feat_num_underscores,
        feat_num_slashes,
        feat_num_digits,
        feat_num_special,
        feat_num_subdomains,
        feat_has_ip,
        feat_has_https,
        feat_suspicious,
        feat_has_at,
        feat_double_slash,
        feat_tld_subdomain,
        feat_shortened,
        feat_entropy,
        feat_digit_ratio,
        feat_upper_ratio,
        feat_path_depth,
    ]


def extract_features_batch(urls) -> np.ndarray:
    """
    Extract features for a list / Series of URLs.

    Parameters
    ----------
    urls : iterable of str

    Returns
    -------
    np.ndarray of shape (n_samples, 22)
    """
    return np.array([extract_features(u) for u in urls], dtype=np.float32)
