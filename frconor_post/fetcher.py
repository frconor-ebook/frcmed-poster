"""Transcript fetching and parsing module."""

import time
from typing import NamedTuple

import requests
from bs4 import BeautifulSoup

from .utils import validate_transcript_url


class TranscriptResult(NamedTuple):
    """Result of transcript fetching."""
    text: str
    word_count: int
    themes: list[str]


def fetch_transcript(url: str, max_retries: int = 3, timeout: int = 30) -> TranscriptResult:
    """Fetch and parse transcript from a URL.

    Args:
        url: The transcript URL (frconor-ebook.github.io)
        max_retries: Maximum number of retry attempts
        timeout: Request timeout in seconds

    Returns:
        TranscriptResult with text, word count, and extracted themes

    Raises:
        ValueError: If URL is invalid
        requests.RequestException: If all retries fail
    """
    if not validate_transcript_url(url):
        raise ValueError(f"Invalid transcript URL: {url}")

    last_error = None

    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            html = response.text
            break
        except requests.RequestException as e:
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            continue
    else:
        raise last_error or requests.RequestException(f"Failed to fetch {url}")

    # Parse HTML
    soup = BeautifulSoup(html, "html.parser")

    # Extract main content - try article tag first, then main, then body
    content = soup.find("article") or soup.find("main") or soup.find("body")

    if not content:
        raise ValueError(f"Could not find main content in {url}")

    # Extract text from paragraphs
    paragraphs = content.find_all("p")
    text_parts = []

    for p in paragraphs:
        text = p.get_text(strip=True)
        # Skip closing prayer (often starts with "I thank you, my God")
        if text.startswith("I thank you, my God"):
            continue
        if text:
            text_parts.append(text)

    full_text = "\n\n".join(text_parts)
    word_count = len(full_text.split())

    # Extract themes (simple keyword extraction)
    themes = extract_themes(full_text)

    return TranscriptResult(
        text=full_text,
        word_count=word_count,
        themes=themes
    )


def extract_themes(text: str) -> list[str]:
    """Extract key themes from transcript text.

    Uses simple keyword frequency analysis to identify main themes.
    """
    # Common spiritual/meditation themes to look for
    theme_keywords = {
        "love": ["love", "loving", "beloved"],
        "peace": ["peace", "peaceful", "calm", "tranquil"],
        "trust": ["trust", "trusting", "faith", "faithful"],
        "guidance": ["guide", "guidance", "lead", "leading", "path"],
        "forgiveness": ["forgive", "forgiveness", "mercy", "merciful"],
        "hope": ["hope", "hopeful", "promise"],
        "prayer": ["pray", "prayer", "praying"],
        "grace": ["grace", "gracious", "blessing"],
        "suffering": ["suffer", "suffering", "pain", "struggle"],
        "healing": ["heal", "healing", "restore", "restoration"],
        "joy": ["joy", "joyful", "happiness", "happy"],
        "silence": ["silence", "silent", "quiet", "stillness"],
        "surrender": ["surrender", "letting go", "release"],
        "belonging": ["belong", "belonging", "home"],
        "protection": ["protect", "protection", "shepherd", "safe"],
        "presence": ["presence", "present", "aware", "awareness"],
        "gratitude": ["grateful", "gratitude", "thankful", "thanks"],
        "humility": ["humble", "humility", "meek"],
    }

    text_lower = text.lower()
    found_themes = []

    for theme, keywords in theme_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                found_themes.append(theme)
                break

    # Return top themes (max 5)
    return found_themes[:5] if found_themes else ["reflection", "meditation"]


def get_transcript_excerpt(text: str, max_words: int = 2000) -> str:
    """Get an excerpt from the transcript for quote generation.

    Tries to include the most meaningful parts of the transcript.
    """
    words = text.split()

    if len(words) <= max_words:
        return text

    # Take roughly the first 60% and last 20% to capture intro and conclusion
    first_portion = int(max_words * 0.7)
    last_portion = max_words - first_portion

    first_words = words[:first_portion]
    last_words = words[-last_portion:]

    excerpt = " ".join(first_words) + "\n\n[...]\n\n" + " ".join(last_words)

    return excerpt
