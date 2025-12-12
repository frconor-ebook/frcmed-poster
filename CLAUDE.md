# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install in development mode
pip install -e .

# Run the CLI
frcmed-post                           # Interactive mode
frcmed-post --help                    # Show all options
frcmed-post --history                 # View post history
frcmed-post --llm gemini              # Use specific LLM (gemini|claude|codex)
frcmed-post --style hopper            # Override art style
```

## Architecture

This is a CLI tool that generates WhatsApp posts for a meditation podcast channel. The workflow:

1. **Input**: User provides Apple Podcasts, Spotify, and transcript URLs
2. **Fetch**: Downloads transcript from GitHub Pages, extracts themes
3. **Quote Generation**: Calls external LLM CLI (gemini/claude/codex via subprocess) to generate 15 hook options
4. **Image Prompt**: Constructs art-style-aware prompt for nano-banana MCP (user runs image generation separately)
5. **Compose**: Assembles final post with shortened URLs
6. **Output**: Copies text to clipboard, logs to history

### Key Modules

| Module | Responsibility |
|--------|----------------|
| `cli.py` | Entry point, orchestrates 6-step workflow with interactive prompts |
| `quote_generator.py` | LLM abstraction - calls gemini/claude/codex CLI, parses numbered hooks |
| `fetcher.py` | HTTP fetch from GitHub Pages, BeautifulSoup parsing, theme extraction |
| `image_generator.py` | Builds image prompts using art style definitions |
| `config.py` | Loads JSON configs, manages art style rotation state |
| `output.py` | Clipboard (pbcopy), file I/O, history logging |

### Configuration

- `config/settings.json` - LLM provider, URL shortener path, output preferences
- `config/art_styles.json` - 8 art styles with prompt elements (elwell, sloan, hopper, sorolla, wyeth, homer, hasui, vermeer)
- `prompts/quote_generation.md` - Template for 15-hook generation with rhetorical styles
- `state/state.json` - Art style rotation index, post count (gitignored)
- `state/post_history.json` - Log of all generated posts (gitignored)

### External Dependencies

The quote generation calls external CLI tools via subprocess:
- `gemini` CLI with `--model` flag
- `claude -p` for Claude Code
- `codex exec` for OpenAI Codex

URL shortening uses an external script at the path configured in `settings.json`.
