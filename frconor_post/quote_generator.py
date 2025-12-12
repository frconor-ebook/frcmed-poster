"""Quote generation using LLM providers (Gemini, Claude, Codex)."""

import re
import subprocess
from typing import NamedTuple

from .config import load_prompt_template, load_settings


class Hook(NamedTuple):
    """A generated hook/quote."""
    number: int
    style: str
    text: str


def generate_quotes(
    episode_title: str,
    transcript_excerpt: str,
    provider: str | None = None
) -> list[Hook]:
    """Generate 15 hooks using the configured LLM provider.

    Args:
        episode_title: Title of the meditation episode
        transcript_excerpt: Excerpt of the transcript text
        provider: LLM provider to use (gemini, claude, codex). If None, uses settings default.

    Returns:
        List of 15 Hook objects
    """
    settings = load_settings()
    llm_config = settings.get("llm", {})

    # Determine provider
    if provider is None:
        provider = llm_config.get("quote_generation", {}).get("provider", "gemini")

    # Load prompt template
    prompt_template = load_prompt_template("quote_generation")

    # Fill in template
    prompt = prompt_template.replace("{episode_title}", episode_title)
    prompt = prompt.replace("{transcript_excerpt}", transcript_excerpt)

    # Generate based on provider
    if provider == "gemini":
        response = _call_gemini(prompt, llm_config)
    elif provider == "claude":
        response = _call_claude(prompt, llm_config)
    elif provider == "codex":
        response = _call_codex(prompt, llm_config)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")

    # Parse response into hooks
    hooks = _parse_hooks(response)

    return hooks


def _call_gemini(prompt: str, config: dict) -> str:
    """Call Gemini CLI for quote generation."""
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
    """Call Claude Code CLI for quote generation."""
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
    """Call Codex CLI for quote generation."""
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


def _parse_hooks(response: str) -> list[Hook]:
    """Parse LLM response into a list of Hook objects.

    Expected format:
    1. [Style]: "hook text"
    2. [Style]: "hook text"
    ...
    """
    hooks = []

    # Pattern to match numbered hooks with optional style labels
    # Matches: 1. [Label]: "text" or 1. "text" or 1. text
    pattern = r'(\d+)\.\s*(?:\[([^\]]+)\]:\s*)?["\']?(.+?)["\']?\s*$'

    lines = response.strip().split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        match = re.match(pattern, line, re.MULTILINE)
        if match:
            number = int(match.group(1))
            style = match.group(2) or _infer_style(number)
            text = match.group(3).strip().strip('"\'')

            hooks.append(Hook(number=number, style=style, text=text))

    # If parsing failed, try a more lenient approach
    if len(hooks) < 5:
        hooks = _parse_hooks_lenient(response)

    return hooks


def _parse_hooks_lenient(response: str) -> list[Hook]:
    """More lenient parsing for hooks that don't follow strict format."""
    hooks = []

    # Look for any numbered lines
    lines = response.strip().split("\n")
    hook_number = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check if line starts with a number
        match = re.match(r'^(\d+)[\.\)]\s*(.+)', line)
        if match:
            hook_number = int(match.group(1))
            text = match.group(2).strip().strip('"\'')
            style = _infer_style(hook_number)
            hooks.append(Hook(number=hook_number, style=style, text=text))

    return hooks


def _infer_style(number: int) -> str:
    """Infer style label from hook number."""
    style_map = {
        1: "Provocative Question",
        2: "Minimalist Moment",
        3: "Witty Reframe",
        4: "Direct Invitation",
        5: "Profound Tease",
        6: "Poignant",
        7: "Poignant",
        8: "Poignant",
        9: "Poignant",
        10: "Poignant",
    }
    return style_map.get(number, "Varied")


def format_hooks_display(hooks: list[Hook]) -> str:
    """Format hooks for display to user."""
    output = []

    current_section = None

    for hook in hooks:
        # Determine section
        if hook.number <= 5:
            section = "CREATIVE STYLES"
        elif hook.number <= 10:
            section = "POIGNANT & EMOTIONALLY DEVASTATING"
        else:
            section = "VARIED TONES"

        # Add section header if changed
        if section != current_section:
            if current_section is not None:
                output.append("")
            output.append(f"\n{section}:")
            output.append("-" * 40)
            current_section = section

        # Format hook
        output.append(f"  {hook.number:2}. [{hook.style}]")
        output.append(f"      \"{hook.text}\"")

    return "\n".join(output)
