"""Output module - clipboard, file saving, and history logging."""

import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from .composer import Post, format_post_text
from .config import (
    advance_art_style_rotation,
    load_history,
    load_settings,
    load_state,
    save_history,
    save_state,
)


def copy_to_clipboard(text: str) -> bool:
    """Copy text to system clipboard.

    Uses pbcopy on macOS, falls back to pyperclip if available.
    Returns True if successful.
    """
    # Try pbcopy first (macOS)
    try:
        process = subprocess.Popen(
            ["pbcopy"],
            stdin=subprocess.PIPE,
            env={"LANG": "en_US.UTF-8"}
        )
        process.communicate(text.encode("utf-8"))
        if process.returncode == 0:
            return True
    except FileNotFoundError:
        pass

    # Fall back to pyperclip
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except ImportError:
        pass
    except Exception:
        pass

    return False


def save_final_image(source_path: str | Path, output_dir: Path) -> Path:
    """Copy the selected image to final_post.png in output directory.

    Args:
        source_path: Path to the selected variation image
        output_dir: Output directory for today's images

    Returns:
        Path to the saved final image
    """
    source = Path(source_path)
    if not source.exists():
        raise FileNotFoundError(f"Source image not found: {source}")

    output_dir.mkdir(parents=True, exist_ok=True)
    dest = output_dir / "final_post.png"

    shutil.copy2(source, dest)
    return dest


def open_in_finder(path: Path) -> bool:
    """Open a file or directory in Finder (macOS).

    Returns True if successful.
    """
    try:
        if path.is_dir():
            subprocess.run(["open", str(path)], check=True)
        else:
            subprocess.run(["open", "-R", str(path)], check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def log_post_to_history(
    post: Post,
    style_id: str,
    style_name: str,
    image_prompt: str | None = None
) -> str:
    """Log a completed post to history.

    Args:
        post: The composed post
        style_id: Art style ID used
        style_name: Art style name
        image_prompt: The image generation prompt used

    Returns:
        The generated post ID
    """
    history = load_history()
    state = load_state()

    # Generate post ID
    today = datetime.now().strftime("%Y-%m-%d")
    post_count = len([p for p in history.get("posts", []) if p.get("id", "").startswith(today)])
    post_id = f"{today}-{post_count + 1:03d}"

    # Create history entry
    entry = {
        "id": post_id,
        "created_at": datetime.now().isoformat(),
        "episode": {
            "title": post.episode_title,
            "apple_url": post.apple_url,
            "spotify_url": post.spotify_url,
            "transcript_url": post.transcript_url,
            "transcript_url_shortened": post.transcript_url_shortened
        },
        "content": {
            "hook": post.hook,
            "full_post_text": format_post_text(post)
        },
        "image": {
            "style": style_name,
            "style_id": style_id,
            "file_path": str(post.image_path) if post.image_path else None,
            "prompt_used": image_prompt
        }
    }

    # Add to history
    if "posts" not in history:
        history["posts"] = []
    history["posts"].append(entry)
    save_history(history)

    # Update state
    state["last_post_date"] = today
    state["total_posts"] = state.get("total_posts", 0) + 1
    save_state(state)

    return post_id


def finalize_post(
    post: Post,
    selected_image_path: Path | None,
    output_dir: Path,
    style_id: str,
    style_name: str,
    image_prompt: str | None = None,
    advance_rotation: bool = True
) -> dict:
    """Finalize a post - save image, copy to clipboard, log to history.

    Args:
        post: The composed post
        selected_image_path: Path to the selected variation image
        output_dir: Output directory
        style_id: Art style ID used
        style_name: Art style name
        image_prompt: The image generation prompt
        advance_rotation: Whether to advance the art style rotation

    Returns:
        Dict with finalization results
    """
    settings = load_settings()
    results = {
        "success": True,
        "image_saved": None,
        "clipboard_copied": False,
        "history_logged": None,
        "finder_opened": False,
        "errors": []
    }

    # Save final image
    if selected_image_path:
        try:
            final_path = save_final_image(selected_image_path, output_dir)
            results["image_saved"] = str(final_path)
        except Exception as e:
            results["errors"].append(f"Failed to save image: {e}")

    # Copy to clipboard
    if settings.get("output", {}).get("copy_to_clipboard", True):
        post_text = format_post_text(post)
        if copy_to_clipboard(post_text):
            results["clipboard_copied"] = True
        else:
            results["errors"].append("Failed to copy to clipboard")

    # Log to history
    try:
        post_id = log_post_to_history(post, style_id, style_name, image_prompt)
        results["history_logged"] = post_id
    except Exception as e:
        results["errors"].append(f"Failed to log to history: {e}")

    # Open in Finder
    if settings.get("output", {}).get("open_finder_after_generation", True):
        if output_dir.exists():
            results["finder_opened"] = open_in_finder(output_dir)

    # Advance rotation
    if advance_rotation:
        try:
            advance_art_style_rotation()
        except Exception as e:
            results["errors"].append(f"Failed to advance rotation: {e}")

    if results["errors"]:
        results["success"] = False

    return results


def format_success_message(results: dict, output_dir: Path) -> str:
    """Format a success message for display."""
    lines = [
        "",
        "═" * 60,
        "  ✓ POST READY",
        "═" * 60,
        ""
    ]

    if results.get("image_saved"):
        lines.append(f"✓ Image saved: {results['image_saved']}")

    if results.get("clipboard_copied"):
        lines.append("✓ Post text copied to clipboard")

    if results.get("history_logged"):
        lines.append(f"✓ Logged to history (ID: {results['history_logged']})")

    lines.append("")
    lines.append("TO POST ON WHATSAPP:")
    lines.append("  1. Open WhatsApp Desktop or Web")
    lines.append("  2. Go to \"Fr. Conor Meditation Updates\" channel")
    lines.append("  3. Click attachment icon → Select image from:")
    lines.append(f"     {output_dir}")
    lines.append("  4. Paste text (Cmd+V) in caption field")
    lines.append("  5. Send!")
    lines.append("")
    lines.append("═" * 60)

    return "\n".join(lines)
