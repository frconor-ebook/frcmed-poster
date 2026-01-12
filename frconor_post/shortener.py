"""URL shortening integration using frcmed_shorten_cli.py."""

import json
import subprocess
from pathlib import Path

from .config import get_cache_path, load_settings


def get_shortened_urls_cache() -> dict[str, str]:
    """Load the shortened URLs cache."""
    cache_file = get_cache_path() / "shortened_urls.json"
    if cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_shortened_urls_cache(cache: dict[str, str]) -> None:
    """Save the shortened URLs cache."""
    cache_file = get_cache_path() / "shortened_urls.json"
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


# Known URL shortener domains - skip shortening if URL is already from these
SHORTENER_DOMAINS = {
    "tinyurl.com",
    "bit.ly",
    "bitly.com",
    "t.co",
    "goo.gl",
    "ow.ly",
    "is.gd",
    "buff.ly",
    "short.io",
}


def is_already_shortened(url: str) -> bool:
    """Check if URL is already from a URL shortener service."""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return parsed.netloc.lower() in SHORTENER_DOMAINS


def shorten_url(url: str, use_cache: bool = True) -> str:
    """Shorten a transcript URL using frcmed_shorten_cli.py.

    Args:
        url: The transcript URL to shorten
        use_cache: Whether to use cached shortened URLs

    Returns:
        Shortened URL or original URL if shortening fails or already shortened
    """
    # Skip if URL is already shortened
    if is_already_shortened(url):
        return url

    settings = load_settings()
    shortener_config = settings.get("url_shortener", {})

    # Check if shortening is enabled
    if not shortener_config.get("enabled", True):
        return url

    # Check cache first
    if use_cache and shortener_config.get("cache_enabled", True):
        cache = get_shortened_urls_cache()
        if url in cache:
            return cache[url]

    # Get script path (expand ~ to home directory)
    script_path = shortener_config.get("script_path")
    if script_path:
        script_path = str(Path(script_path).expanduser())
    if not script_path or not Path(script_path).exists():
        print(f"Warning: URL shortener script not found at {script_path}")
        return url

    try:
        result = subprocess.run(
            ["python", script_path, "--no-copy", url],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            shortened = result.stdout.strip()
            if shortened and shortened.startswith("http"):
                # Cache the result
                if use_cache and shortener_config.get("cache_enabled", True):
                    cache = get_shortened_urls_cache()
                    cache[url] = shortened
                    save_shortened_urls_cache(cache)
                return shortened
            else:
                print(f"Warning: Unexpected shortener output: {shortened}")
                return url
        else:
            print(f"Warning: URL shortening failed: {result.stderr}")
            return url

    except subprocess.TimeoutExpired:
        print("Warning: URL shortening timed out")
        return url
    except FileNotFoundError:
        print(f"Warning: Python not found or script not executable")
        return url
    except Exception as e:
        print(f"Warning: URL shortener error: {e}")
        return url
