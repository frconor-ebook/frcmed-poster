"""Post composition and preview module."""

from typing import NamedTuple


class Post(NamedTuple):
    """A composed WhatsApp post."""
    hook: str
    episode_title: str
    apple_url: str
    spotify_url: str
    transcript_url: str
    transcript_url_shortened: str
    image_path: str | None


POST_TEMPLATE = """{hook}

Today's meditation: *{episode_title}*

🎧 Apple: {apple_url}
Spotify: {spotify_url}

📖 Transcript: {transcript_url}"""


def compose_post(
    hook: str,
    episode_title: str,
    apple_url: str,
    spotify_url: str,
    transcript_url_shortened: str,
    image_path: str | None = None,
    transcript_url_original: str | None = None,
) -> Post:
    """Compose a complete WhatsApp post.

    Args:
        hook: The selected hook text
        episode_title: Episode title
        apple_url: Apple Podcasts URL
        spotify_url: Spotify URL
        transcript_url_shortened: Shortened transcript URL
        image_path: Path to selected image (optional)
        transcript_url_original: Original transcript URL (for logging)

    Returns:
        Composed Post object
    """
    return Post(
        hook=hook,
        episode_title=episode_title,
        apple_url=apple_url,
        spotify_url=spotify_url,
        transcript_url=transcript_url_original or transcript_url_shortened,
        transcript_url_shortened=transcript_url_shortened,
        image_path=image_path
    )


def format_post_text(post: Post) -> str:
    """Format post for clipboard/WhatsApp.

    Uses the shortened transcript URL in the output.
    """
    return POST_TEMPLATE.format(
        hook=post.hook,
        episode_title=post.episode_title,
        apple_url=post.apple_url,
        spotify_url=post.spotify_url,
        transcript_url=post.transcript_url_shortened
    )


def format_post_preview(post: Post) -> str:
    """Format post for terminal preview display."""
    text = format_post_text(post)

    # Calculate character count
    char_count = len(text)

    # Build preview box
    border = "─" * 60
    image_info = f"[IMAGE: {post.image_path}]" if post.image_path else "[No image selected]"

    preview = f"""
┌{border}┐
│ FINAL POST PREVIEW
├{border}┤

  {image_info}

{_indent_text(text, 2)}

├{border}┤
│ Character count: {char_count}
└{border}┘
"""
    return preview


def _indent_text(text: str, spaces: int) -> str:
    """Indent each line of text by given spaces."""
    indent = " " * spaces
    lines = text.split("\n")
    return "\n".join(indent + line for line in lines)


def validate_post(post: Post) -> list[str]:
    """Validate post and return list of warnings."""
    warnings = []

    # Check hook length
    if len(post.hook) > 280:
        warnings.append(f"Hook is {len(post.hook)} characters (recommended max: 280)")

    # Check total length
    full_text = format_post_text(post)
    if len(full_text) > 1000:
        warnings.append(f"Total post is {len(full_text)} characters (may be long for WhatsApp)")

    # Check URLs
    if not post.apple_url.startswith("http"):
        warnings.append("Apple URL doesn't look valid")
    if not post.spotify_url.startswith("http"):
        warnings.append("Spotify URL doesn't look valid")

    return warnings
