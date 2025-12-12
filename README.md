# Fr. Conor Daily Post Generator

CLI tool for generating WhatsApp posts for the "Fr. Conor Meditation Updates" channel.

## Features

- **Quote Generation**: Generates 15 creative hooks from meditation transcripts using LLMs (Gemini, Claude, or Codex)
- **Art Style Rotation**: 8 painter styles (Hopper, Vermeer, Sorolla, etc.) rotate automatically
- **Comic Strip Generation**: 4-panel comic strips with 7 artistic styles and thought-provoking dialogue
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

### Full Post Generation (`frcmed-post`)

```bash
# Interactive mode (recommended)
frcmed-post

# Specify LLM provider
frcmed-post -l gemini
frcmed-post -l claude

# Override art style (elwell|sloan|hopper|sorolla|wyeth|homer|hasui|vermeer)
frcmed-post -s hopper

# Skip quote generation with your own quote
frcmed-post -q "Your custom quote here"

# Provide URLs directly
frcmed-post -a "https://podcasts.apple.com/..." \
            -p "https://open.spotify.com/..." \
            -t "https://frconor-ebook.github.io/..."

# View post history
frcmed-post -H
```

### Standalone Image Generation (`frcmed-image`)

Generate meditation images directly from a quote without the full post workflow:

```bash
# Basic usage (quote only, random style)
frcmed-image -q "Peace begins with a pause."

# With transcript for theme extraction
frcmed-image -q "..." -t "https://frconor-ebook.github.io/..."

# Specify art style (elwell|sloan|hopper|sorolla|wyeth|homer|hasui|vermeer)
frcmed-image -q "..." -s hopper

# Use specific LLM for concept generation
frcmed-image -q "..." -l claude
```

### 4-Panel Comic Strip Generation (`frcmed-comic`)

Generate 4-panel comic strips with thought-provoking dialogue from meditation transcripts:

```bash
# Basic usage (transcript required, random style)
frcmed-comic -t "https://frconor-ebook.github.io/..."

# Specify comic style (moebius|watercolor|baroque|expressionist|minimalist|deco|woodcut)
frcmed-comic -t URL -s moebius

# Use specific LLM for concept generation
frcmed-comic -t URL -l claude
```

## Workflows

### `frcmed-post` (Full Post)

1. **Input URLs** - Provide Apple Podcasts, Spotify, and transcript URLs
2. **Fetch Transcript** - Downloads and parses the meditation transcript
3. **Generate Quotes** - LLM generates 15 hooks (or use `--quote` to skip)
4. **Select Quote** - Choose from the generated options
5. **Build Image Prompt** - Constructs prompt based on quote and art style
6. **Compose Post** - Assembles final WhatsApp post
7. **Output** - Copies text to clipboard, saves to history

### `frcmed-image` (Standalone Image)

1. **Input** - Provide quote (required) and transcript URL (optional)
2. **Extract Themes** - Parses transcript for themes (if URL provided)
3. **Select Style** - Use specified style or random selection
4. **Generate Concepts** - LLM generates 3 image scene concepts
5. **Pick Concept** - Choose from concepts or regenerate
6. **Generate Image** - Creates image via Claude CLI + nano-banana MCP

### `frcmed-comic` (4-Panel Comic)

1. **Input** - Provide transcript URL (required)
2. **Fetch Transcript** - Downloads and parses the meditation transcript
3. **Select Style** - Use specified comic style or random selection
4. **Generate Concepts** - LLM generates 4 comic strip concepts with dialogue
5. **Pick Concept** - Choose from concepts (1-4), regenerate (r), or quit (q)
6. **Build Prompt** - Constructs 4-panel comic prompt with dialogue instructions
7. **Generate Comic** - Creates comic via Claude CLI + nano-banana MCP

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

### Comic Styles (`config/comic_styles.json`)

Seven comic strip styles with dialogue support:
- `moebius` - Painterly European Graphic Novel (Moebius, Schuiten, Gibrat)
- `watercolor` - Watercolor Impressionist (Jillian Tamaki, Ghibli)
- `baroque` - Neo-Baroque Chiaroscuro (Rembrandt, Doré)
- `expressionist` - Expressionist Ink & Brush (Steadman, Egon Schiele)
- `minimalist` - Minimalist Conceptual (Tom Gauld, Anders Nilsen)
- `deco` - Art-Deco/Art-Nouveau Fusion (Mucha, Klimt)
- `woodcut` - Woodcut-Inspired Digital Engraving (Dürer, Lynd Ward)

## Project Structure

```
frcmed-poster/
├── frconor_post/              # Main Python package
│   ├── cli.py                 # frcmed-post entry point
│   ├── image_cli.py           # frcmed-image entry point
│   ├── comic_cli.py           # frcmed-comic entry point
│   ├── quote_generator.py     # LLM hook generation
│   ├── concept_generator.py   # LLM image concept generation
│   ├── comic_generator.py     # LLM comic concept generation
│   ├── fetcher.py             # Transcript fetching
│   ├── image_generator.py     # Image prompt construction
│   ├── composer.py            # Post composition
│   └── output.py              # Clipboard & history
├── config/                    # Configuration files
├── prompts/                   # LLM prompt templates
├── state/                     # Runtime state (gitignored)
└── output/                    # Generated images (gitignored)
```

## License

Private use only.
