"""Image generation module - constructs prompts for nano-banana MCP."""

from datetime import date
from pathlib import Path
from typing import NamedTuple

from .config import (
    get_current_art_style,
    get_output_dir,
    load_settings,
    get_art_style_by_id,
)


class ImagePrompt(NamedTuple):
    """Constructed image prompt ready for generation."""
    prompt: str
    style_id: str
    style_name: str
    model_tier: str
    resolution: str
    aspect_ratio: str
    n: int


def build_image_prompt(
    quote: str,
    themes: list[str],
    style_id: str | None = None
) -> ImagePrompt:
    """Build an image generation prompt based on quote and style.

    Args:
        quote: The selected hook text
        themes: Themes extracted from transcript
        style_id: Optional specific style ID. If None, uses current rotation style.

    Returns:
        ImagePrompt ready for nano-banana MCP
    """
    settings = load_settings()
    image_config = settings.get("image_generation", {})

    # Get art style
    if style_id:
        style = get_art_style_by_id(style_id)
        if not style:
            raise ValueError(f"Unknown art style: {style_id}")
    else:
        style = get_current_art_style()

    # Extract style elements
    prompt_elements = style.get("prompt_elements", {})
    style_desc = prompt_elements.get("style_description", "")
    color_palette = prompt_elements.get("color_palette", "")
    composition = prompt_elements.get("composition", "")
    avoid = prompt_elements.get("avoid", "")
    mood_keywords = style.get("mood_keywords", [])
    cultural_fit = style.get("cultural_fit", [])

    # Build the prompt
    prompt_parts = [
        f"Create an image {style_desc}.",
        "",
        "Scene Requirements:",
        f"- The scene should visually evoke the feeling of: \"{quote}\"",
        f"- Key themes to incorporate: {', '.join(themes)}",
        f"- Cultural context: {', '.join(cultural_fit)}",
        f"- Emotional mood: {', '.join(mood_keywords)}",
        "",
        "Visual Specifications:",
        f"- Color palette: {color_palette}",
        f"- Composition approach: {composition}",
        f"- Must avoid: {avoid}",
        "",
        "Technical Requirements:",
        "- Apply rule of thirds, position key elements along grid lines",
        "- 1-3 human figures maximum as primary subjects",
        "- No text, watermarks, or signatures in the image",
        "- Secular scene only (no explicitly religious iconography)",
    ]

    prompt = "\n".join(prompt_parts)

    return ImagePrompt(
        prompt=prompt,
        style_id=style.get("id", "unknown"),
        style_name=style.get("name", "Unknown"),
        model_tier=image_config.get("model_tier", "pro"),
        resolution=image_config.get("resolution", "high"),
        aspect_ratio=image_config.get("aspect_ratio", "4:3"),
        n=image_config.get("variations_count", 3)
    )


def get_output_path() -> Path:
    """Get the output directory path (~/Desktop)."""
    return get_output_dir()


def ensure_output_directory() -> Path:
    """Return the output directory (~/Desktop)."""
    return get_output_path()


def get_variation_filename(variation_number: int) -> str:
    """Get filename for an image variation."""
    return f"variation_{variation_number}.png"


def get_final_filename() -> str:
    """Get filename for the final selected image."""
    return "final_post.png"


def format_image_prompt_display(image_prompt: ImagePrompt) -> str:
    """Format image prompt info for display."""
    return f"""
Art Style: {image_prompt.style_name}
Model: {image_prompt.model_tier}
Resolution: {image_prompt.resolution}
Aspect Ratio: {image_prompt.aspect_ratio}
Variations: {image_prompt.n}

Prompt:
{'-' * 40}
{image_prompt.prompt}
{'-' * 40}
"""
