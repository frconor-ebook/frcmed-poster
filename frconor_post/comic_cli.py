"""CLI entry point for Fr. Conor Comic Strip Generator."""

import argparse
import json
import random
import sys
from pathlib import Path

from . import __version__
from .config import load_settings
from .fetcher import fetch_transcript, get_transcript_excerpt
from .comic_generator import generate_comic_concepts, format_comic_concepts_display
from .image_generator import (
    build_comic_prompt,
    ensure_output_directory,
    format_image_prompt_display,
    generate_images,
)


def print_header():
    """Print the application header."""
    print("=" * 60)
    print("  FR. CONOR 4-PANEL COMIC GENERATOR")
    print("=" * 60)
    print()


def print_section(title: str):
    """Print a section header."""
    print()
    print("-" * 60)
    print(f"  {title}")
    print("-" * 60)
    print()


def get_input(prompt: str, default: str = "") -> str:
    """Get user input with optional default."""
    if default:
        result = input(f"{prompt} [{default}]: ").strip()
        return result if result else default
    return input(f"{prompt}: ").strip()


def load_comic_styles() -> dict:
    """Load comic styles from config file."""
    config_path = Path(__file__).parent.parent / "config" / "comic_styles.json"
    with open(config_path, "r") as f:
        return json.load(f)


def get_comic_style_by_id(style_id: str) -> dict | None:
    """Get a comic style by ID."""
    styles = load_comic_styles()
    for style in styles.get("styles", []):
        if style.get("id") == style_id:
            return style
    return None


def get_random_comic_style() -> dict:
    """Get a random comic style."""
    styles = load_comic_styles()
    style_list = styles.get("styles", [])
    if not style_list:
        raise ValueError("No comic styles configured")
    return random.choice(style_list)


def run_workflow(args):
    """Run the comic generation workflow."""
    print_header()
    print("Generate 4-panel comic strips from meditation transcripts.")
    print()

    settings = load_settings()

    # Determine LLM provider
    llm_provider = args.llm or settings.get("llm", {}).get("quote_generation", {}).get("provider", "gemini")
    print(f"LLM for concept generation: {llm_provider}")
    print()

    # Step 1: Fetch transcript
    print_section("STEP 1: FETCH TRANSCRIPT")

    transcript_url = args.transcript
    print(f"Transcript URL: {transcript_url}")

    try:
        print("  Fetching transcript...")
        transcript = fetch_transcript(transcript_url)
        themes = transcript.themes
        print(f"  Word count: {transcript.word_count}")
        print(f"  Extracted themes: {', '.join(themes)}")
    except Exception as e:
        print(f"  Error: Could not fetch transcript: {e}")
        sys.exit(1)

    # Get transcript excerpt for concept generation
    transcript_excerpt = get_transcript_excerpt(transcript.text)

    # Step 2: Get comic style
    print_section("STEP 2: COMIC STYLE")

    all_styles = load_comic_styles().get("styles", [])

    if args.style:
        style = get_comic_style_by_id(args.style)
        if not style:
            print(f"Unknown style: {args.style}")
            print(f"Available styles: {', '.join(s['id'] for s in all_styles)}")
            sys.exit(1)
        print(f"Using specified style: {style['name']}")
    else:
        style = get_random_comic_style()
        print(f"Randomly selected style: {style['name']}")

    print(f"  Artists: {', '.join(style.get('artists', []))}")
    print()

    # Step 3: Generate concepts
    print_section("STEP 3: COMIC CONCEPTS")

    try:
        print(f"Generating 4 comic strip concepts using {llm_provider}...")
        concepts = generate_comic_concepts(themes, transcript_excerpt, style, llm_provider)
        print(f"Generated {len(concepts)} concepts")
        print()
        print(format_comic_concepts_display(concepts))
    except Exception as e:
        print(f"Failed to generate concepts: {e}")
        print("  You may need to configure the LLM CLI tool.")
        sys.exit(1)

    # Step 4: User selection
    print()
    selected_concept = None

    while selected_concept is None:
        choice = get_input("Enter concept number (1-4), [r]egenerate, or [q]uit")

        if choice.lower() == 'q':
            print("Cancelled.")
            sys.exit(0)
        elif choice.lower() == 'r':
            print("\nRegenerating concepts...")
            concepts = generate_comic_concepts(themes, transcript_excerpt, style, llm_provider)
            print(format_comic_concepts_display(concepts))
        else:
            try:
                num = int(choice)
                if 1 <= num <= len(concepts):
                    selected_concept = concepts[num - 1]
                    print(f"\nSelected: [{selected_concept.title}]")
                else:
                    print(f"Please enter a number between 1 and {len(concepts)}")
            except ValueError:
                print("Invalid input. Enter a number, 'r', or 'q'.")

    # Step 5: Build final prompt
    print_section("STEP 4: COMIC PROMPT")

    image_prompt = build_comic_prompt(selected_concept, style)
    print(format_image_prompt_display(image_prompt))

    output_dir = ensure_output_directory()
    print(f"Images will be saved to: {output_dir}")
    print()

    # Step 6: Generate comic
    generate = get_input("Generate comic images now? [y/n]", "y")
    if generate.lower() == 'y':
        print()
        print("Generating comic via Claude CLI (this may take a minute)...")
        success = generate_images(image_prompt)
        if success:
            print("  Comic generated successfully!")
        else:
            print("  Comic generation failed. You can generate manually later.")
    else:
        print()
        print("Skipping comic generation.")
        print("To generate later, copy the prompt above and run:")
        print(f"  claude -p \"Generate {image_prompt.n} images with: [prompt]\"")

    print()
    print("Done!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Fr. Conor 4-Panel Comic Generator - Generate comic strips from meditation transcripts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  frcmed-comic -t "https://frconor-ebook.github.io/..."
  frcmed-comic -t URL -s moebius
  frcmed-comic -t URL -l claude

Comic styles: moebius, watercolor, baroque, expressionist, minimalist, deco, woodcut
        """
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    parser.add_argument(
        "-t", "--transcript",
        metavar="URL",
        required=True,
        help="Transcript URL (required)"
    )

    parser.add_argument(
        "-s", "--style",
        metavar="ID",
        choices=["moebius", "watercolor", "baroque", "expressionist", "minimalist", "deco", "woodcut"],
        help="Comic style: moebius, watercolor, baroque, expressionist, minimalist, deco, woodcut. Random if not specified."
    )

    parser.add_argument(
        "-l", "--llm",
        choices=["gemini", "claude", "codex"],
        help="LLM provider for concept generation"
    )

    args = parser.parse_args()
    run_workflow(args)


if __name__ == "__main__":
    main()
