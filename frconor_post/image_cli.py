"""CLI entry point for Fr. Conor Image Generator."""

import argparse
import random
import sys

from . import __version__
from .config import (
    get_art_style_by_id,
    load_art_styles,
    load_settings,
)
from .fetcher import fetch_transcript
from .concept_generator import generate_concepts, format_concepts_display
from .image_generator import (
    build_image_prompt_from_concept,
    ensure_output_directory,
    format_image_prompt_display,
    generate_images,
)


def print_header():
    """Print the application header."""
    print("=" * 60)
    print("  FR. CONOR IMAGE GENERATOR")
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


def get_random_style() -> dict:
    """Get a random art style from the rotation list."""
    styles = load_art_styles()
    rotation = styles.get("rotation", [])
    if not rotation:
        raise ValueError("No art styles configured in rotation")
    return random.choice(rotation)


def run_workflow(args):
    """Run the image generation workflow."""
    print_header()
    print("Generate meditation images from a quote.")
    print()

    settings = load_settings()

    # Determine LLM provider
    llm_provider = args.llm or settings.get("llm", {}).get("quote_generation", {}).get("provider", "gemini")
    print(f"LLM for concept generation: {llm_provider}")
    print()

    # Step 1: Validate inputs
    print_section("STEP 1: INPUT")

    quote = args.quote
    print(f"Quote: \"{quote}\"")

    # Step 2: Fetch transcript (optional)
    themes = []
    if args.transcript:
        print()
        print(f"Transcript URL: {args.transcript}")
        try:
            print("  Fetching transcript...")
            transcript = fetch_transcript(args.transcript)
            themes = transcript.themes
            print(f"  Extracted themes: {', '.join(themes)}")
        except Exception as e:
            print(f"  Warning: Could not fetch transcript: {e}")
            print("  Proceeding without themes.")
    else:
        print()
        print("No transcript URL provided - using quote only for concept generation.")

    # Step 3: Get art style
    print_section("STEP 2: ART STYLE")

    all_styles = load_art_styles().get("rotation", [])

    if args.style:
        style = get_art_style_by_id(args.style)
        if not style:
            print(f"Unknown style: {args.style}")
            print(f"Available styles: {', '.join(s['id'] for s in all_styles)}")
            sys.exit(1)
        print(f"Using specified style: {style['name']}")
    else:
        style = get_random_style()
        print(f"Randomly selected style: {style['name']}")

    print(f"  Mood keywords: {', '.join(style.get('mood_keywords', []))}")
    print()

    # Step 4: Generate concepts
    print_section("STEP 3: IMAGE CONCEPTS")

    try:
        print(f"Generating 3 concepts using {llm_provider}...")
        concepts = generate_concepts(quote, themes, style, llm_provider)
        print(f"Generated {len(concepts)} concepts")
        print()
        print(format_concepts_display(concepts))
    except Exception as e:
        print(f"Failed to generate concepts: {e}")
        print("  You may need to configure the LLM CLI tool.")
        sys.exit(1)

    # Step 5: User selection
    print()
    selected_concept = None

    while selected_concept is None:
        choice = get_input("Enter concept number (1-3), [r]egenerate, or [q]uit")

        if choice.lower() == 'q':
            print("Cancelled.")
            sys.exit(0)
        elif choice.lower() == 'r':
            print("\nRegenerating concepts...")
            concepts = generate_concepts(quote, themes, style, llm_provider)
            print(format_concepts_display(concepts))
        else:
            try:
                num = int(choice)
                if 1 <= num <= len(concepts):
                    selected_concept = concepts[num - 1]
                    print(f"\nSelected: [{selected_concept.setting}]")
                else:
                    print(f"Please enter a number between 1 and {len(concepts)}")
            except ValueError:
                print("Invalid input. Enter a number, 'r', or 'q'.")

    # Step 6: Build final prompt
    print_section("STEP 4: IMAGE PROMPT")

    image_prompt = build_image_prompt_from_concept(selected_concept, style)
    print(format_image_prompt_display(image_prompt))

    output_dir = ensure_output_directory()
    print(f"Images will be saved to: {output_dir}")
    print()

    # Step 7: Generate image
    generate = get_input("Generate images now? [y/n]", "y")
    if generate.lower() == 'y':
        print()
        print("Generating images via Claude CLI (this may take a minute)...")
        success = generate_images(image_prompt)
        if success:
            print("  Images generated successfully!")
        else:
            print("  Image generation failed. You can generate manually later.")
    else:
        print()
        print("Skipping image generation.")
        print("To generate later, copy the prompt above and run:")
        print(f"  claude -p \"Generate {image_prompt.n} images with: [prompt]\"")

    print()
    print("Done!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Fr. Conor Image Generator - Generate meditation images from a quote",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  frcmed-image --quote "Peace begins with a pause."
  frcmed-image --quote "..." --transcript https://...
  frcmed-image --quote "..." --style hopper
  frcmed-image --quote "..." --llm claude
        """
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    parser.add_argument(
        "--quote",
        metavar="TEXT",
        required=True,
        help="Quote to visualize (required)"
    )

    parser.add_argument(
        "--transcript",
        metavar="URL",
        help="Transcript URL for theme extraction (optional)"
    )

    parser.add_argument(
        "--style",
        metavar="ID",
        help="Art style ID (e.g., hopper, vermeer). Random if not specified."
    )

    parser.add_argument(
        "--llm",
        choices=["gemini", "claude", "codex"],
        help="LLM provider for concept generation"
    )

    args = parser.parse_args()
    run_workflow(args)


if __name__ == "__main__":
    main()
