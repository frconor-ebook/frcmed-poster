"""Configuration loading and state management."""

import json
from pathlib import Path
from typing import Any


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def load_json(filepath: Path) -> dict[str, Any]:
    """Load a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(filepath: Path, data: dict[str, Any]) -> None:
    """Save data to a JSON file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_settings() -> dict[str, Any]:
    """Load settings from config/settings.json."""
    settings_path = get_project_root() / "config" / "settings.json"
    return load_json(settings_path)


def load_art_styles() -> dict[str, Any]:
    """Load art styles from config/art_styles.json."""
    styles_path = get_project_root() / "config" / "art_styles.json"
    return load_json(styles_path)


def load_prompt_template(name: str) -> str:
    """Load a prompt template from prompts/ directory."""
    prompt_path = get_project_root() / "prompts" / f"{name}.md"
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def get_state_path() -> Path:
    """Get the path to state.json."""
    return get_project_root() / "state" / "state.json"


def get_history_path() -> Path:
    """Get the path to post_history.json."""
    return get_project_root() / "state" / "post_history.json"


def load_state() -> dict[str, Any]:
    """Load state from state/state.json, creating default if not exists."""
    state_path = get_state_path()
    if state_path.exists():
        return load_json(state_path)
    return {
        "style_rotation_index": 0,
        "last_post_date": None,
        "total_posts": 0
    }


def save_state(state: dict[str, Any]) -> None:
    """Save state to state/state.json."""
    save_json(get_state_path(), state)


def load_history() -> dict[str, Any]:
    """Load post history from state/post_history.json, creating default if not exists."""
    history_path = get_history_path()
    if history_path.exists():
        return load_json(history_path)
    return {"posts": []}


def save_history(history: dict[str, Any]) -> None:
    """Save post history to state/post_history.json."""
    save_json(get_history_path(), history)


def get_current_art_style() -> dict[str, Any]:
    """Get the current art style based on rotation index."""
    state = load_state()
    styles = load_art_styles()
    index = state.get("style_rotation_index", 0)
    rotation = styles.get("rotation", [])
    if not rotation:
        raise ValueError("No art styles configured in art_styles.json")
    return rotation[index % len(rotation)]


def advance_art_style_rotation() -> dict[str, Any]:
    """Advance to the next art style in rotation and return it."""
    state = load_state()
    styles = load_art_styles()
    rotation = styles.get("rotation", [])
    if not rotation:
        raise ValueError("No art styles configured in art_styles.json")

    current_index = state.get("style_rotation_index", 0)
    next_index = (current_index + 1) % len(rotation)
    state["style_rotation_index"] = next_index
    save_state(state)

    return rotation[next_index]


def get_art_style_by_id(style_id: str) -> dict[str, Any] | None:
    """Get a specific art style by its ID."""
    styles = load_art_styles()
    for style in styles.get("rotation", []):
        if style.get("id") == style_id:
            return style
    return None


def get_output_dir() -> Path:
    """Get the output directory for generated images."""
    settings = load_settings()
    output_dir = settings.get("output", {}).get("image_directory", "~/Desktop")
    return Path(output_dir).expanduser()


def get_cache_path() -> Path:
    """Get the cache directory path."""
    return get_project_root() / "cache"
