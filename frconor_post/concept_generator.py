"""Image concept generation using LLM providers (Gemini, Claude, Codex)."""

import re
import subprocess
from typing import NamedTuple

from .config import load_prompt_template, load_settings


class Concept(NamedTuple):
    """A generated image concept."""
    number: int
    setting: str
    scene: str
    mood: str
    elements: str


def generate_concepts(
    quote: str,
    themes: list[str],
    style: dict,
    provider: str | None = None
) -> list[Concept]:
    """Generate 3 image concepts using the configured LLM provider.

    Args:
        quote: The quote to visualize
        themes: List of themes extracted from transcript (can be empty)
        style: Art style dict from art_styles.json
        provider: LLM provider to use (gemini, claude, codex). If None, uses settings default.

    Returns:
        List of 3 Concept objects
    """
    settings = load_settings()
    llm_config = settings.get("llm", {})

    # Determine provider
    if provider is None:
        provider = llm_config.get("quote_generation", {}).get("provider", "gemini")

    # Load prompt template
    prompt_template = load_prompt_template("concept_generation")

    # Extract style elements
    prompt_elements = style.get("prompt_elements", {})
    style_name = style.get("name", "Unknown")
    style_description = prompt_elements.get("style_description", "")
    color_palette = prompt_elements.get("color_palette", "")
    composition = prompt_elements.get("composition", "")

    # Format themes
    themes_str = ", ".join(themes) if themes else "general meditation, peace, reflection"

    # Fill in template
    prompt = prompt_template.replace("{quote}", quote)
    prompt = prompt.replace("{themes}", themes_str)
    prompt = prompt.replace("{style_name}", style_name)
    prompt = prompt.replace("{style_description}", style_description)
    prompt = prompt.replace("{color_palette}", color_palette)
    prompt = prompt.replace("{composition}", composition)

    # Generate based on provider
    if provider == "gemini":
        response = _call_gemini(prompt, llm_config)
    elif provider == "claude":
        response = _call_claude(prompt, llm_config)
    elif provider == "codex":
        response = _call_codex(prompt, llm_config)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")

    # Parse response into concepts
    concepts = _parse_concepts(response)

    return concepts


def _call_gemini(prompt: str, config: dict) -> str:
    """Call Gemini CLI for concept generation."""
    provider_config = config.get("providers", {}).get("gemini", {})
    command = provider_config.get("command", "gemini")
    model_flag = provider_config.get("model_flag", "--model")
    model = config.get("quote_generation", {}).get("model", "gemini-2.5-pro")

    try:
        result = subprocess.run(
            [command, prompt, model_flag, model],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            raise RuntimeError(f"Gemini CLI error: {result.stderr}")

        return result.stdout

    except FileNotFoundError:
        raise RuntimeError("Gemini CLI not found. Install with: pip install google-generativeai")


def _call_claude(prompt: str, config: dict) -> str:
    """Call Claude Code CLI for concept generation."""
    provider_config = config.get("providers", {}).get("claude", {})
    command = provider_config.get("command", "claude")
    prompt_flag = provider_config.get("prompt_flag", "-p")

    try:
        result = subprocess.run(
            [command, prompt_flag, prompt],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            raise RuntimeError(f"Claude CLI error: {result.stderr}")

        return result.stdout

    except FileNotFoundError:
        raise RuntimeError("Claude CLI not found.")


def _call_codex(prompt: str, config: dict) -> str:
    """Call Codex CLI for concept generation."""
    provider_config = config.get("providers", {}).get("codex", {})
    command = provider_config.get("command", "codex")
    subcommand = provider_config.get("subcommand", "exec")

    try:
        result = subprocess.run(
            [command, subcommand, prompt],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            raise RuntimeError(f"Codex CLI error: {result.stderr}")

        return result.stdout

    except FileNotFoundError:
        raise RuntimeError("Codex CLI not found. Install with: npm install -g @openai/codex")


def _parse_concepts(response: str) -> list[Concept]:
    """Parse LLM response into a list of Concept objects.

    Expected format:
    1. [Setting Title]
       Scene: description
       Mood: words
       Elements: items
    """
    concepts = []

    # Split by concept numbers
    # Pattern matches: 1. [Title] or 1. Title
    concept_pattern = r'(\d+)\.\s*\[?([^\]\n]+)\]?'

    # Find all concept headers
    lines = response.strip().split("\n")
    current_concept = None
    current_data = {"scene": "", "mood": "", "elements": ""}

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check for new concept header
        header_match = re.match(concept_pattern, line)
        if header_match:
            # Save previous concept if exists
            if current_concept is not None:
                concepts.append(Concept(
                    number=current_concept["number"],
                    setting=current_concept["setting"],
                    scene=current_data["scene"].strip(),
                    mood=current_data["mood"].strip(),
                    elements=current_data["elements"].strip()
                ))

            # Start new concept
            current_concept = {
                "number": int(header_match.group(1)),
                "setting": header_match.group(2).strip().strip("[]")
            }
            current_data = {"scene": "", "mood": "", "elements": ""}
            continue

        # Parse concept fields
        if current_concept is not None:
            if line.lower().startswith("scene:"):
                current_data["scene"] = line[6:].strip()
            elif line.lower().startswith("mood:"):
                current_data["mood"] = line[5:].strip()
            elif line.lower().startswith("elements:"):
                current_data["elements"] = line[9:].strip()
            elif current_data["scene"] and not current_data["mood"]:
                # Continuation of scene
                current_data["scene"] += " " + line

    # Save last concept
    if current_concept is not None:
        concepts.append(Concept(
            number=current_concept["number"],
            setting=current_concept["setting"],
            scene=current_data["scene"].strip(),
            mood=current_data["mood"].strip(),
            elements=current_data["elements"].strip()
        ))

    # Fallback if parsing failed
    if len(concepts) < 3:
        concepts = _parse_concepts_lenient(response)

    return concepts[:3]  # Ensure max 3


def _parse_concepts_lenient(response: str) -> list[Concept]:
    """More lenient parsing for concepts that don't follow strict format."""
    concepts = []

    # Split by numbered items
    parts = re.split(r'\n(?=\d+\.)', response)

    for i, part in enumerate(parts):
        part = part.strip()
        if not part:
            continue

        # Extract number
        num_match = re.match(r'^(\d+)\.', part)
        if not num_match:
            continue

        number = int(num_match.group(1))

        # Try to extract setting from first line
        first_line = part.split("\n")[0]
        setting_match = re.search(r'\[([^\]]+)\]', first_line)
        if setting_match:
            setting = setting_match.group(1)
        else:
            # Use first few words after number
            setting = re.sub(r'^\d+\.\s*', '', first_line)[:50]

        # Extract remaining content as scene
        remaining = "\n".join(part.split("\n")[1:])
        scene = remaining.strip() if remaining else first_line

        concepts.append(Concept(
            number=number,
            setting=setting,
            scene=scene[:200],  # Limit length
            mood="contemplative",
            elements="figure, light, space"
        ))

    return concepts


def format_concepts_display(concepts: list[Concept]) -> str:
    """Format concepts for display to user."""
    output = []
    output.append("IMAGE CONCEPTS:")
    output.append("=" * 50)

    for concept in concepts:
        output.append(f"\n  {concept.number}. [{concept.setting}]")
        output.append(f"     Scene: {concept.scene}")
        output.append(f"     Mood: {concept.mood}")
        output.append(f"     Elements: {concept.elements}")

    output.append("")
    output.append("=" * 50)

    return "\n".join(output)
