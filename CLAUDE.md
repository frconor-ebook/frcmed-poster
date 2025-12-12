# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install in development mode
pip install -e .

# Full post generation (frcmed-post)
frcmed-post                    # Interactive mode
frcmed-post --help             # Show all options
frcmed-post -H                 # View post history
frcmed-post -l gemini          # Use specific LLM (gemini|claude|codex)
frcmed-post -s hopper          # Override art style
frcmed-post -q "Your quote"    # Skip quote generation

# Standalone image generation (frcmed-image)
frcmed-image -q "Peace begins with a pause."   # Quote only, random style
frcmed-image -q "..." -t URL                   # With theme extraction
frcmed-image -q "..." -s hopper                # Specific art style
frcmed-image -q "..." -l claude                # Use Claude for concepts

# Shorthand flags:
# -q/--quote, -t/--transcript, -s/--style, -l/--llm
# -a/--apple, -p/--spotify, -H/--history (frcmed-post only)
```

## Architecture

This is a CLI tool that generates WhatsApp posts for a meditation podcast channel.

### `frcmed-post` Workflow (Full Post)

1. **Input**: User provides Apple Podcasts, Spotify, and transcript URLs
2. **Fetch**: Downloads transcript from GitHub Pages, extracts themes
3. **Quote Generation**: Calls LLM CLI to generate 15 hooks (or use `--quote` to skip)
4. **Image Prompt**: Constructs art-style-aware prompt for nano-banana MCP
5. **Compose**: Assembles final post with shortened URLs
6. **Output**: Copies text to clipboard, logs to history

### `frcmed-image` Workflow (Standalone Image)

1. **Input**: Quote (required) + transcript URL (optional)
2. **Themes**: Extract from transcript if URL provided
3. **Style**: Use specified style or random from rotation
4. **Concepts**: LLM generates 3 image scene concepts
5. **Selection**: User picks concept or regenerates
6. **Generation**: Creates image via Claude CLI + nano-banana MCP

### Key Modules

| Module | Responsibility |
|--------|----------------|
| `cli.py` | `frcmed-post` entry point, orchestrates full post workflow |
| `image_cli.py` | `frcmed-image` entry point, standalone image generation |
| `quote_generator.py` | LLM abstraction - generates 15 hooks from transcript |
| `concept_generator.py` | LLM abstraction - generates 3 image concepts from quote |
| `fetcher.py` | HTTP fetch from GitHub Pages, BeautifulSoup parsing, theme extraction |
| `image_generator.py` | Builds image prompts using art style definitions |
| `config.py` | Loads JSON configs, manages art style rotation state |
| `output.py` | Clipboard (pbcopy), file I/O, history logging |

### Configuration

- `config/settings.json` - LLM provider, URL shortener path, output preferences
- `config/art_styles.json` - 8 art styles with prompt elements (elwell, sloan, hopper, sorolla, wyeth, homer, hasui, vermeer)
- `prompts/quote_generation.md` - Template for 15-hook generation with rhetorical styles
- `prompts/concept_generation.md` - Template for 3 image concept generation
- `state/state.json` - Art style rotation index, post count (gitignored)
- `state/post_history.json` - Log of all generated posts (gitignored)

### External Dependencies

The quote generation calls external CLI tools via subprocess:
- `gemini` CLI with `--model` flag
- `claude -p` for Claude Code
- `codex exec` for OpenAI Codex

URL shortening uses an external script at the path configured in `settings.json`.
