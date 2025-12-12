"""Comic strip concept generation using LLM providers (Gemini, Claude, Codex)."""

import re
import subprocess
from typing import NamedTuple

from .config import load_prompt_template, load_settings


class ComicConcept(NamedTuple):
    """A generated 4-panel comic strip concept with dialogue."""
    number: int
    title: str
    arc: str
    panel_1: str
    dialogue_1: str
    panel_2: str
    dialogue_2: str
    panel_3: str
    dialogue_3: str
    panel_4: str
    dialogue_4: str


def generate_comic_concepts(
    themes: list[str],
    transcript_excerpt: str,
    style: dict,
    provider: str | None = None
) -> list[ComicConcept]:
    """Generate 4 comic strip concepts using the configured LLM provider.

    Args:
        themes: List of themes extracted from transcript
        transcript_excerpt: Excerpt of the transcript text
        style: Comic style dict from comic_styles.json
        provider: LLM provider to use (gemini, claude, codex). If None, uses settings default.

    Returns:
        List of 4 ComicConcept objects
    """
    settings = load_settings()
    llm_config = settings.get("llm", {})

    # Determine provider
    if provider is None:
        provider = llm_config.get("quote_generation", {}).get("provider", "gemini")

    # Load prompt template
    prompt_template = load_prompt_template("comic_generation")

    # Extract style elements
    prompt_elements = style.get("prompt_elements", {})
    style_name = style.get("name", "Unknown")
    style_description = prompt_elements.get("style_description", "")

    # Format themes
    themes_str = ", ".join(themes) if themes else "meditation, peace, reflection"

    # Fill in template
    prompt = prompt_template.replace("{themes}", themes_str)
    prompt = prompt.replace("{transcript_excerpt}", transcript_excerpt[:2000])
    prompt = prompt.replace("{style_name}", style_name)
    prompt = prompt.replace("{style_description}", style_description)

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
    concepts = _parse_comic_concepts(response)

    return concepts


def _call_gemini(prompt: str, config: dict) -> str:
    """Call Gemini CLI for comic concept generation."""
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
    """Call Claude Code CLI for comic concept generation."""
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
    """Call Codex CLI for comic concept generation."""
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


def _parse_comic_concepts(response: str) -> list[ComicConcept]:
    """Parse LLM response into a list of ComicConcept objects.

    Expected format:
    1. [Comic Title]
       Arc: description
       Panel 1: description
       Dialogue 1: SPEECH/THOUGHT/CAPTION: "text"
       Panel 2: description
       Dialogue 2: ...
       etc.
    """
    concepts = []

    # Split by concept numbers
    lines = response.strip().split("\n")
    current_concept = None
    current_data = {
        "arc": "",
        "panel_1": "", "dialogue_1": "",
        "panel_2": "", "dialogue_2": "",
        "panel_3": "", "dialogue_3": "",
        "panel_4": "", "dialogue_4": ""
    }

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check for new concept header (e.g., "1. [Title]" or "1. Title")
        header_match = re.match(r'^(\d+)\.\s*\[?([^\]\n]+)\]?$', line)
        if header_match:
            # Save previous concept if exists
            if current_concept is not None:
                concepts.append(ComicConcept(
                    number=current_concept["number"],
                    title=current_concept["title"],
                    arc=current_data["arc"].strip(),
                    panel_1=current_data["panel_1"].strip(),
                    dialogue_1=current_data["dialogue_1"].strip(),
                    panel_2=current_data["panel_2"].strip(),
                    dialogue_2=current_data["dialogue_2"].strip(),
                    panel_3=current_data["panel_3"].strip(),
                    dialogue_3=current_data["dialogue_3"].strip(),
                    panel_4=current_data["panel_4"].strip(),
                    dialogue_4=current_data["dialogue_4"].strip()
                ))

            # Start new concept
            current_concept = {
                "number": int(header_match.group(1)),
                "title": header_match.group(2).strip().strip("[]")
            }
            current_data = {
                "arc": "",
                "panel_1": "", "dialogue_1": "",
                "panel_2": "", "dialogue_2": "",
                "panel_3": "", "dialogue_3": "",
                "panel_4": "", "dialogue_4": ""
            }
            continue

        # Parse concept fields
        if current_concept is not None:
            line_lower = line.lower()
            if line_lower.startswith("arc:"):
                current_data["arc"] = line[4:].strip()
            elif line_lower.startswith("panel 1:"):
                current_data["panel_1"] = line[8:].strip()
            elif line_lower.startswith("dialogue 1:"):
                current_data["dialogue_1"] = line[11:].strip()
            elif line_lower.startswith("panel 2:"):
                current_data["panel_2"] = line[8:].strip()
            elif line_lower.startswith("dialogue 2:"):
                current_data["dialogue_2"] = line[11:].strip()
            elif line_lower.startswith("panel 3:"):
                current_data["panel_3"] = line[8:].strip()
            elif line_lower.startswith("dialogue 3:"):
                current_data["dialogue_3"] = line[11:].strip()
            elif line_lower.startswith("panel 4:"):
                current_data["panel_4"] = line[8:].strip()
            elif line_lower.startswith("dialogue 4:"):
                current_data["dialogue_4"] = line[11:].strip()

    # Save last concept
    if current_concept is not None:
        concepts.append(ComicConcept(
            number=current_concept["number"],
            title=current_concept["title"],
            arc=current_data["arc"].strip(),
            panel_1=current_data["panel_1"].strip(),
            dialogue_1=current_data["dialogue_1"].strip(),
            panel_2=current_data["panel_2"].strip(),
            dialogue_2=current_data["dialogue_2"].strip(),
            panel_3=current_data["panel_3"].strip(),
            dialogue_3=current_data["dialogue_3"].strip(),
            panel_4=current_data["panel_4"].strip(),
            dialogue_4=current_data["dialogue_4"].strip()
        ))

    # Fallback if parsing failed
    if len(concepts) < 4:
        concepts = _parse_comic_concepts_lenient(response)

    return concepts[:4]  # Ensure max 4


def _parse_comic_concepts_lenient(response: str) -> list[ComicConcept]:
    """More lenient parsing for concepts that don't follow strict format."""
    concepts = []

    # Split by numbered items
    parts = re.split(r'\n(?=\d+\.)', response)

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Extract number
        num_match = re.match(r'^(\d+)\.', part)
        if not num_match:
            continue

        number = int(num_match.group(1))

        # Try to extract title from first line
        first_line = part.split("\n")[0]
        title_match = re.search(r'\[([^\]]+)\]', first_line)
        if title_match:
            title = title_match.group(1)
        else:
            title = re.sub(r'^\d+\.\s*', '', first_line)[:50]

        # Extract panel descriptions
        panels = ["", "", "", ""]
        panel_pattern = r'panel\s*(\d+)\s*:\s*(.+?)(?=panel\s*\d+|dialogue|$)'
        panel_matches = re.findall(panel_pattern, part, re.IGNORECASE | re.DOTALL)
        for panel_num, panel_desc in panel_matches:
            idx = int(panel_num) - 1
            if 0 <= idx < 4:
                panels[idx] = panel_desc.strip()[:200]

        # Extract dialogues
        dialogues = ["", "", "", ""]
        dialogue_pattern = r'dialogue\s*(\d+)\s*:\s*(.+?)(?=panel\s*\d+|dialogue\s*\d+|$)'
        dialogue_matches = re.findall(dialogue_pattern, part, re.IGNORECASE | re.DOTALL)
        for dial_num, dial_text in dialogue_matches:
            idx = int(dial_num) - 1
            if 0 <= idx < 4:
                dialogues[idx] = dial_text.strip()[:200]

        # Extract arc if present
        arc_match = re.search(r'arc:\s*(.+?)(?=panel|$)', part, re.IGNORECASE | re.DOTALL)
        arc = arc_match.group(1).strip()[:150] if arc_match else "A contemplative journey"

        concepts.append(ComicConcept(
            number=number,
            title=title,
            arc=arc,
            panel_1=panels[0] or "Opening scene",
            dialogue_1=dialogues[0] or "CAPTION: \"...\"",
            panel_2=panels[1] or "Development",
            dialogue_2=dialogues[1] or "CAPTION: \"...\"",
            panel_3=panels[2] or "The turn",
            dialogue_3=dialogues[2] or "CAPTION: \"...\"",
            panel_4=panels[3] or "Resolution",
            dialogue_4=dialogues[3] or "CAPTION: \"...\""
        ))

    return concepts


def format_comic_concepts_display(concepts: list[ComicConcept]) -> str:
    """Format comic concepts for display to user."""
    output = []
    output.append("4-PANEL COMIC CONCEPTS:")
    output.append("=" * 60)

    for concept in concepts:
        output.append(f"\n  {concept.number}. [{concept.title}]")
        output.append(f"     Arc: {concept.arc}")
        output.append(f"     Panel 1: {concept.panel_1[:60]}...")
        output.append(f"       -> {concept.dialogue_1[:60]}...")
        output.append(f"     Panel 2: {concept.panel_2[:60]}...")
        output.append(f"       -> {concept.dialogue_2[:60]}...")
        output.append(f"     Panel 3: {concept.panel_3[:60]}...")
        output.append(f"       -> {concept.dialogue_3[:60]}...")
        output.append(f"     Panel 4: {concept.panel_4[:60]}...")
        output.append(f"       -> {concept.dialogue_4[:60]}...")

    output.append("")
    output.append("=" * 60)

    return "\n".join(output)
