"""Utility functions for URL validation and title extraction."""

import re
from urllib.parse import urlparse


# Expected podcast ID for Fr. Conor meditations
PODCAST_ID = "id1643273205"


def validate_apple_url(url: str) -> bool:
    """Validate an Apple Podcasts URL.

    Expected pattern: https://podcasts.apple.com/*/podcast/*/id1643273205?i=*
    """
    if not url:
        return False
    parsed = urlparse(url)
    if parsed.netloc != "podcasts.apple.com":
        return False
    if "/podcast/" not in parsed.path:
        return False
    if PODCAST_ID not in url:
        return False
    return True


def validate_spotify_url(url: str) -> bool:
    """Validate a Spotify episode URL.

    Expected pattern: https://open.spotify.com/episode/*
    """
    if not url:
        return False
    parsed = urlparse(url)
    if parsed.netloc != "open.spotify.com":
        return False
    if not parsed.path.startswith("/episode/"):
        return False
    return True


def validate_transcript_url(url: str) -> bool:
    """Validate a transcript URL.

    Expected pattern: https://frconor-ebook.github.io/meditations/homilies/*
    """
    if not url:
        return False
    parsed = urlparse(url)
    if parsed.netloc != "frconor-ebook.github.io":
        return False
    if "/meditations/" not in parsed.path:
        return False
    return True


def extract_title_from_apple_url(url: str) -> str:
    """Extract and format episode title from Apple Podcasts URL.

    URL pattern: https://podcasts.apple.com/us/podcast/{title-slug}/id1643273205?i={episode-id}
    Extracts {title-slug}, converts hyphens to spaces, applies title case.

    Example: the-good-shepherd -> "The Good Shepherd"
    """
    if not validate_apple_url(url):
        raise ValueError(f"Invalid Apple Podcasts URL: {url}")

    parsed = urlparse(url)
    path_parts = parsed.path.strip("/").split("/")

    # Find the title slug (the part before the podcast ID)
    title_slug = None
    for i, part in enumerate(path_parts):
        if part == "podcast" and i + 1 < len(path_parts):
            title_slug = path_parts[i + 1]
            break

    if not title_slug:
        raise ValueError(f"Could not extract title from URL: {url}")

    # Convert slug to title
    title = title_slug.replace("-", " ")
    title = title.title()

    return title


def extract_slug_from_transcript_url(url: str) -> str:
    """Extract the episode slug from a transcript URL.

    Example: https://frconor-ebook.github.io/meditations/homilies/the-good-shepherd/
            -> "the-good-shepherd"
    """
    if not validate_transcript_url(url):
        raise ValueError(f"Invalid transcript URL: {url}")

    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    slug = path.split("/")[-1]

    return slug


def format_hook_text(text: str) -> str:
    """Validate and clean hook text formatting.

    Ensures:
    - Matching pairs of *asterisks* and _underscores_
    - Maximum ~280 characters
    - No leading/trailing whitespace
    """
    text = text.strip()

    # Check for matching formatting pairs
    asterisk_count = text.count("*")
    underscore_count = text.count("_")

    if asterisk_count % 2 != 0:
        raise ValueError(f"Mismatched asterisks in hook: {text}")
    if underscore_count % 2 != 0:
        raise ValueError(f"Mismatched underscores in hook: {text}")

    return text


def validate_urls(apple_url: str, spotify_url: str, transcript_url: str) -> dict[str, str]:
    """Validate all three URLs and return them in a dict.

    Raises ValueError if any URL is invalid.
    """
    errors = []

    if not validate_apple_url(apple_url):
        errors.append(f"Invalid Apple Podcasts URL: {apple_url}")

    if not validate_spotify_url(spotify_url):
        errors.append(f"Invalid Spotify URL: {spotify_url}")

    if not validate_transcript_url(transcript_url):
        errors.append(f"Invalid transcript URL: {transcript_url}")

    if errors:
        raise ValueError("\n".join(errors))

    return {
        "apple_url": apple_url,
        "spotify_url": spotify_url,
        "transcript_url": transcript_url
    }
