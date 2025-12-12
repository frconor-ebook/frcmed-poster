# Fr. Conor Daily Post Generator

CLI tool for generating WhatsApp posts for the "Fr. Conor Meditation Updates" channel.

## Features

- **Quote Generation**: Generates 15 creative hooks from meditation transcripts using LLMs (Gemini, Claude, or Codex)
- **Art Style Rotation**: 8 painter styles (Hopper, Vermeer, Sorolla, etc.) rotate automatically
- **Image Prompts**: Constructs detailed prompts for AI image generation
- **URL Shortening**: Integrates with TinyURL for transcript links
- **Post History**: Tracks all generated posts with full metadata

## Installation

```bash
# Clone the repository
git clone https://github.com/frconor-ebook/frcmed-poster.git
cd frcmed-poster

# Install in development mode
pip install -e .
```

### Requirements

- Python 3.10+
- One of the following LLM CLIs installed:
  - `gemini` (recommended) - [Gemini CLI](https://github.com/google-gemini/gemini-cli)
  - `claude` - [Claude Code](https://claude.ai/code)
  - `codex` - [OpenAI Codex CLI](https://github.com/openai/codex)

## Usage

```bash
# Interactive mode (recommended)
frconor-post

# Specify LLM provider
frconor-post --llm gemini
frconor-post --llm claude

# Override art style
frconor-post --style hopper

# Provide URLs directly
frconor-post --apple "https://podcasts.apple.com/..." \
             --spotify "https://open.spotify.com/..." \
             --transcript "https://frconor-ebook.github.io/..."

# View post history
frconor-post --history
```

## Workflow

1. **Input URLs** - Provide Apple Podcasts, Spotify, and transcript URLs
2. **Fetch Transcript** - Downloads and parses the meditation transcript
3. **Generate Quotes** - LLM generates 15 hooks in various creative styles
4. **Select Quote** - Choose from the generated options
5. **Build Image Prompt** - Constructs prompt based on quote and art style
6. **Compose Post** - Assembles final WhatsApp post
7. **Output** - Copies text to clipboard, saves to history

## Configuration

### Settings (`config/settings.json`)

- LLM provider and model selection
- URL shortener script path
- Output directory preferences
- Image generation parameters

### Art Styles (`config/art_styles.json`)

Eight painter styles with prompt elements:
- `elwell` - Frederick William Elwell (Victorian domestic)
- `sloan` - John French Sloan (Ashcan School)
- `hopper` - Edward Hopper (solitude, light/shadow)
- `sorolla` - Joaquín Sorolla (Mediterranean light)
- `wyeth` - Andrew Wyeth (rural America)
- `homer` - Winslow Homer (maritime watercolor)
- `hasui` - Kawase Hasui (Japanese Shin Hanga)
- `vermeer` - Johannes Vermeer (Dutch Golden Age)

## Project Structure

```
frcmed-poster/
├── frconor_post/          # Main Python package
│   ├── cli.py             # CLI entry point
│   ├── quote_generator.py # LLM integration
│   ├── fetcher.py         # Transcript fetching
│   ├── image_generator.py # Image prompt construction
│   ├── composer.py        # Post composition
│   └── output.py          # Clipboard & history
├── config/                # Configuration files
├── prompts/               # LLM prompt templates
├── state/                 # Runtime state (gitignored)
└── output/                # Generated images (gitignored)
```

## License

Private use only.
