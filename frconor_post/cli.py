"""CLI entry point for Fr. Conor Daily Post Generator."""

import argparse
import sys
from pathlib import Path

from . import __version__
from .composer import compose_post, format_post_preview, format_post_text, validate_post
from .config import (
    get_current_art_style,
    get_art_style_by_id,
    load_art_styles,
    load_history,
    load_settings,
    load_state,
)
from .fetcher import fetch_transcript, get_transcript_excerpt
from .image_generator import (
    build_image_prompt,
    ensure_output_directory,
    format_image_prompt_display,
    generate_images,
)
from .output import finalize_post, format_success_message
from .quote_generator import format_hooks_display, generate_quotes
from .shortener import shorten_url
from .utils import extract_title_from_apple_url, validate_urls


def print_header():
    """Print the application header."""
    print("═" * 60)
    print("  FR. CONOR DAILY POST GENERATOR")
    print("═" * 60)
    print()


def print_section(title: str):
    """Print a section header."""
    print()
    print("─" * 60)
    print(f"  {title}")
    print("─" * 60)
    print()


def get_input(prompt: str, default: str = "") -> str:
    """Get user input with optional default."""
    if default:
        result = input(f"{prompt} [{default}]: ").strip()
        return result if result else default
    return input(f"{prompt}: ").strip()


def show_history():
    """Display post history."""
    history = load_history()
    posts = history.get("posts", [])

    if not posts:
        print("No posts in history yet.")
        return

    print_header()
    print(f"Post History ({len(posts)} posts)")
    print("─" * 60)

    for post in reversed(posts[-10:]):  # Show last 10
        print(f"\n{post.get('id', 'Unknown')}: {post.get('episode', {}).get('title', 'Unknown')}")
        print(f"  Style: {post.get('image', {}).get('style', 'Unknown')}")
        hook = post.get('content', {}).get('hook', '')
        if len(hook) > 60:
            hook = hook[:57] + "..."
        print(f"  Hook: \"{hook}\"")


def run_workflow(args):
    """Run the main post generation workflow."""
    print_header()
    print("Ready to create today's meditation post!")
    print()

    settings = load_settings()
    state = load_state()

    # Determine LLM provider
    llm_provider = args.llm or settings.get("llm", {}).get("quote_generation", {}).get("provider", "gemini")
    print(f"LLM for quote generation: {llm_provider}")
    print()

    # Step 1: Get URLs
    print_section("STEP 1: INPUT URLS")

    if args.apple and args.spotify and args.transcript:
        apple_url = args.apple
        spotify_url = args.spotify
        transcript_url = args.transcript
        print(f"Using provided URLs:")
        print(f"  Apple: {apple_url}")
        print(f"  Spotify: {spotify_url}")
        print(f"  Transcript: {transcript_url}")
    else:
        print("Please provide the three URLs:\n")
        apple_url = get_input("1. Apple Podcasts URL")
        spotify_url = get_input("2. Spotify URL")
        transcript_url = get_input("3. Transcript URL")

    # Validate URLs
    try:
        validate_urls(apple_url, spotify_url, transcript_url)
        print("\n✓ URLs validated")
    except ValueError as e:
        print(f"\n✗ URL validation failed: {e}")
        sys.exit(1)

    # Step 2: Fetch and parse
    print_section("STEP 2: PROCESSING")

    # Extract title
    try:
        episode_title = extract_title_from_apple_url(apple_url)
        print(f"✓ Extracted title: \"{episode_title}\"")
    except ValueError as e:
        print(f"✗ Failed to extract title: {e}")
        sys.exit(1)

    # Fetch transcript
    try:
        print("  Fetching transcript...")
        transcript = fetch_transcript(transcript_url)
        print(f"✓ Fetched transcript ({transcript.word_count} words)")
        print(f"✓ Analyzed themes: {', '.join(transcript.themes)}")
    except Exception as e:
        print(f"✗ Failed to fetch transcript: {e}")
        sys.exit(1)

    # Shorten URL
    print("  Shortening transcript URL...")
    transcript_url_shortened = shorten_url(transcript_url)
    if transcript_url_shortened != transcript_url:
        print(f"✓ Shortened URL: {transcript_url_shortened}")
    else:
        print("  (Using original URL)")

    # Step 3: Generate quotes
    print_section("STEP 3: QUOTE OPTIONS")

    transcript_excerpt = get_transcript_excerpt(transcript.text)

    try:
        print(f"Generating 15 hooks using {llm_provider}...")
        hooks = generate_quotes(episode_title, transcript_excerpt, llm_provider)
        print(f"✓ Generated {len(hooks)} hooks")
        print()
        print(format_hooks_display(hooks))
    except Exception as e:
        print(f"✗ Failed to generate quotes: {e}")
        print("  You may need to configure the LLM CLI tool.")
        sys.exit(1)

    # User selection
    print()
    print("─" * 40)
    selected_hook = None

    while selected_hook is None:
        choice = get_input("Enter hook number (1-15), [r]egenerate, or [q]uit")

        if choice.lower() == 'q':
            print("Cancelled.")
            sys.exit(0)
        elif choice.lower() == 'r':
            print("\nRegenerating hooks...")
            hooks = generate_quotes(episode_title, transcript_excerpt, llm_provider)
            print(format_hooks_display(hooks))
        else:
            try:
                num = int(choice)
                if 1 <= num <= len(hooks):
                    selected_hook = hooks[num - 1]
                    print(f"\n✓ Selected: \"{selected_hook.text}\"")
                else:
                    print(f"Please enter a number between 1 and {len(hooks)}")
            except ValueError:
                print("Invalid input. Enter a number, 'r', or 'q'.")

    # Step 4: Image generation
    print_section("STEP 4: IMAGE GENERATION")

    # Determine art style
    all_styles = load_art_styles().get("rotation", [])
    rotation_index = state.get("style_rotation_index", 0)
    default_style = get_current_art_style()

    if args.style:
        # Use command-line specified style
        style = get_art_style_by_id(args.style)
        if not style:
            print(f"Unknown style: {args.style}")
            print(f"Available styles: {', '.join(s['id'] for s in all_styles)}")
            sys.exit(1)
    else:
        # Interactive style selection with rotation default
        print("Available art styles:")
        for i, s in enumerate(all_styles, 1):
            default_marker = " (default - rotation)" if s['id'] == default_style['id'] else ""
            print(f"  {i}. {s['name']}{default_marker}")
        print()

        style_choice = get_input(f"Select style [1-{len(all_styles)}] or Enter for default", "")

        if style_choice:
            try:
                idx = int(style_choice) - 1
                if 0 <= idx < len(all_styles):
                    style = all_styles[idx]
                    print(f"  Selected: {style['name']}")
                else:
                    print(f"  Invalid choice, using default: {default_style['name']}")
                    style = default_style
            except ValueError:
                # Try matching by ID
                style = get_art_style_by_id(style_choice)
                if style:
                    print(f"  Selected: {style['name']}")
                else:
                    print(f"  Invalid choice, using default: {default_style['name']}")
                    style = default_style
        else:
            style = default_style
            print(f"  Using rotation default: {style['name']}")

    print()
    print(f"Art style: {style['name']}")
    print(f"Theme alignment: {', '.join(style.get('mood_keywords', []))}")
    print()

    # Build image prompt
    image_prompt = build_image_prompt(
        quote=selected_hook.text,
        themes=transcript.themes,
        style_id=style.get("id")
    )

    print(format_image_prompt_display(image_prompt))

    output_dir = ensure_output_directory()
    print(f"Images will be saved to: {output_dir}")
    print()

    # Generate images using Claude CLI + nano-banana MCP
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
        print("To generate later, run:")
        print(f"  claude -p \"Generate {image_prompt.n} images with: [prompt above]\"")

    print()
    proceed = get_input("Proceed to compose post? [y/n]", "y")
    if proceed.lower() != 'y':
        print("Stopping here.")
        sys.exit(0)

    # Step 5: Compose post
    print_section("STEP 5: COMPOSE & PREVIEW")

    post = compose_post(
        hook=selected_hook.text,
        episode_title=episode_title,
        apple_url=apple_url,
        spotify_url=spotify_url,
        transcript_url_shortened=transcript_url_shortened,
        transcript_url_original=transcript_url,
        image_path=None  # No image selected yet
    )

    print(format_post_preview(post))

    # Validate
    warnings = validate_post(post)
    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"  ⚠ {w}")

    # User approval
    print()
    choice = get_input("Approve? [y]es, [e]dit hook, [q]uit", "y")

    if choice.lower() == 'q':
        print("Cancelled.")
        sys.exit(0)
    elif choice.lower() == 'e':
        new_hook = get_input("Enter new hook text")
        post = compose_post(
            hook=new_hook,
            episode_title=episode_title,
            apple_url=apple_url,
            spotify_url=spotify_url,
            transcript_url_shortened=transcript_url_shortened,
            transcript_url_original=transcript_url,
        )
        print(format_post_preview(post))

    # Step 6: Finalize
    print_section("STEP 6: FINALIZE")

    results = finalize_post(
        post=post,
        selected_image_path=None,  # No image for now
        output_dir=output_dir,
        style_id=style.get("id", "unknown"),
        style_name=style.get("name", "Unknown"),
        image_prompt=image_prompt.prompt,
        advance_rotation=True
    )

    print(format_success_message(results, output_dir))

    if results.get("errors"):
        print("\nWarnings:")
        for err in results["errors"]:
            print(f"  ⚠ {err}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Fr. Conor Daily Post Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  frcmed-post                    # Interactive mode
  frcmed-post --llm gemini       # Use Gemini for quotes
  frcmed-post --style hopper     # Use Edward Hopper style
  frcmed-post --history          # View post history
        """
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    parser.add_argument(
        "--llm",
        choices=["gemini", "claude", "codex"],
        help="LLM provider for quote generation"
    )

    parser.add_argument(
        "--apple",
        metavar="URL",
        help="Apple Podcasts URL"
    )

    parser.add_argument(
        "--spotify",
        metavar="URL",
        help="Spotify URL"
    )

    parser.add_argument(
        "--transcript",
        metavar="URL",
        help="Transcript URL"
    )

    parser.add_argument(
        "--style",
        metavar="ID",
        help="Art style ID (e.g., hopper, vermeer, hasui)"
    )

    parser.add_argument(
        "--history",
        action="store_true",
        help="Show post history"
    )

    args = parser.parse_args()

    if args.history:
        show_history()
    else:
        run_workflow(args)


if __name__ == "__main__":
    main()
