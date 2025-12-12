# Product Requirements Document (PRD)
# Fr. Conor Daily Post Generator

**Version:** 1.0
**Last Updated:** December 12, 2025
**Author:** Edward Wijaya
**Implementer:** Claude Code

---

## Table of Contents

1. [Overview](#1-overview)
2. [Goals & Non-Goals](#2-goals--non-goals)
3. [User Workflow](#3-user-workflow)
4. [Technical Architecture](#4-technical-architecture)
5. [Detailed Requirements](#5-detailed-requirements)
6. [Data Models & Configuration](#6-data-models--configuration)
7. [Prompts & Templates](#7-prompts--templates)
8. [File Structure](#8-file-structure)
9. [Implementation Phases](#9-implementation-phases)
10. [Testing Criteria](#10-testing-criteria)
11. [Appendices](#11-appendices)

---

## 1. Overview

### 1.1 Background

The product owner maintains a WhatsApp Channel called "Fr. Conor Meditation Updates" where daily meditation content is shared. The channel features:
- An AI-generated artistic image reflecting the meditation's theme
- A poetic/engaging quote or hook derived from the meditation transcript
- Links to Apple Podcasts, Spotify, and the transcript

Currently, this is a fully manual process requiring:
1. Checking for new meditation episodes
2. Reading transcripts and crafting quotes
3. Generating artistic images using specific art styles
4. Composing and posting to WhatsApp

### 1.2 Product Vision

Create a CLI-based automation tool that handles 95% of the creative work while preserving human curation through approval checkpoints. The final WhatsApp posting remains manual (copy-paste) to avoid infrastructure complexity.

### 1.3 Target User

The product owner, who will run the tool daily via terminal command.

---

## 2. Goals & Non-Goals

### 2.1 Goals

| Goal | Priority | Success Metric |
|------|----------|----------------|
| Automate quote generation from transcript | P0 | Generate 15 quality hooks in <30 seconds |
| Automate image generation | P0 | Generate 3 images per session with retry logic |
| Provide approval workflow | P0 | User can select/reject at each stage |
| Rotate through art styles | P1 | 8+ styles in rotation, state persisted |
| Output ready-to-paste content | P0 | Image saved, text copied to clipboard |
| Track posting history | P2 | Log of all past posts for reference |

### 2.2 Non-Goals

| Non-Goal | Reason |
|----------|--------|
| Automated WhatsApp posting | Requires server infrastructure (WAHA/paid APIs) |
| Scheduled/cron-based execution | User prefers manual trigger with approval |
| Multi-platform posting | Focus on WhatsApp only |
| Transcript URL auto-discovery | User will provide URL directly |

---

## 3. User Workflow

### 3.1 High-Level Flow

**Command-Line Usage:**
```bash
# Default usage (uses settings.json LLM preference)
frconor-post

# Specify LLM for quote generation
frconor-post --llm gemini
frconor-post --llm codex
frconor-post --llm claude

# Quick mode: provide URLs directly
frconor-post --apple "https://podcasts.apple.com/..." \
             --spotify "https://open.spotify.com/..." \
             --transcript "https://frconor-ebook.github.io/..."

# Override art style for this session
frconor-post --style hopper

# View post history
frconor-post --history

# Show help
frconor-post --help
```

**Flow Diagram:**

```
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 1: USER INPUT                                                 │
│  User runs: claude -p "meditation post"                             │
│  User provides 3 URLs when prompted                                 │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 2: FETCH & PARSE                                              │
│  • Extract episode title from Apple Podcasts URL                    │
│  • Fetch full transcript from GitHub Pages                          │
│  • Parse and clean transcript text                                  │
│  • Shorten transcript URL via frcmed_shorten_cli.py                 │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 3: GENERATE QUOTE OPTIONS                                     │
│  • Apply 5 creative styles with rhetorical devices                  │
│  • Generate 5 poignant/emotionally devastating hooks                │
│  • Generate 5 varied alternatives                                   │
│  • Display all 15 options to user                                   │
│                                                                     │
│  >>> USER APPROVAL CHECKPOINT <<<                                   │
│  User selects one hook OR requests regeneration                     │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 4: GENERATE IMAGE OPTIONS                                     │
│  • Select next art style from rotation queue                        │
│  • Build detailed image prompt based on quote + style               │
│  • Call nano-banana MCP to generate 3 images                        │
│  • If generation fails → retry with backup style                    │
│  • Display 3 images to user                                         │
│                                                                     │
│  >>> USER APPROVAL CHECKPOINT <<<                                   │
│  User selects one image OR requests regeneration                    │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 5: COMPOSE & PREVIEW                                          │
│  • Assemble final post: Image + Quote + Title + Links               │
│  • Use shortened transcript URL (tinyurl.com/frcmed-*)              │
│  • Display formatted preview                                        │
│                                                                     │
│  >>> USER APPROVAL CHECKPOINT <<<                                   │
│  User approves OR requests edits                                    │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 6: OUTPUT FOR MANUAL POSTING                                  │
│  • Save final image to ~/Desktop/frconor-posts/                     │
│  • Copy post text to system clipboard                               │
│  • Log post to history file                                         │
│  • Display success message with instructions                        │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Detailed Interaction Example

```
═══════════════════════════════════════════════════════════════════════
  FR. CONOR DAILY POST GENERATOR
═══════════════════════════════════════════════════════════════════════

Ready to create today's meditation post!

LLM for quote generation: gemini (gemini-3-pro-preview)
  [Press Enter to continue, or type 'codex' / 'claude' to switch]

Please provide the three URLs:

1. Apple Podcasts URL: https://podcasts.apple.com/us/podcast/the-good-shepherd/id1643273205?i=1000638229472

2. Spotify URL: https://open.spotify.com/episode/5BA0ueDmbor2rs8Ps7vM53?si=WbYy9V_HQIS3_xWzsWI8Rg

3. Transcript URL: https://frconor-ebook.github.io/meditations/homilies/the-good-shepherd/

───────────────────────────────────────────────────────────────────────
  PROCESSING
───────────────────────────────────────────────────────────────────────

✓ Extracted title: "The Good Shepherd"
✓ Fetched transcript (2,847 words)
✓ Analyzed key themes: trust, guidance, belonging, protection
✓ Shortened transcript URL: https://tinyurl.com/frcmed-goodshepherd

───────────────────────────────────────────────────────────────────────
  QUOTE OPTIONS (15 hooks)
───────────────────────────────────────────────────────────────────────

STYLE 1 — Provocative Question (Antithesis/Paradox):
  1. "Why does the _safest_ place often feel like surrender?"
  2. "What if being *found* requires admitting you were lost?"

STYLE 2 — Minimalist Moment (Scesis Onomaton/Diacope):
  3. "Known. Seen. *Called by name.*"
  4. "A voice. _Your_ voice. Finally heard."

STYLE 3 — Witty Reframe (Catachresis/Paradox):
  5. "Sheep aren't stupid—they just know who to *trust*."
  6. "The shepherd's job isn't to _chase_. It's to wait."

STYLE 4 — Direct Invitation (Isocolon/Alliteration):
  7. "Stop striving. Start *following*."
  8. "Rest in the pasture. Rise with *purpose*."

STYLE 5 — Profound Tease (Chiasmus/Fourteenth Rule):
  9. "There's a voice that knows your name before you _speak_ it."
  10. "He doesn't lead where He hasn't *walked*."

POIGNANT / EMOTIONALLY DEVASTATING:
  11. "When you've wandered so far you forgot the way back—*He hasn't.*"
  12. "The shepherd doesn't count the 99. He counts *you*."
  13. "Lost isn't a location. It's forgetting someone is _looking_."
  14. "Every scar on His hands? A sheep who almost didn't make it."
  15. "You think you're hiding. He thinks you're *found*."

───────────────────────────────────────────────────────────────────────

Enter hook number (1-15), or:
  [r] Regenerate all hooks
  [m] Modify a specific hook

Your choice: 12

✓ Selected: "The shepherd doesn't count the 99. He counts *you*."

───────────────────────────────────────────────────────────────────────
  IMAGE GENERATION
───────────────────────────────────────────────────────────────────────

Today's art style (rotation #4): Edward Hopper
Theme alignment: solitude, contemplation, warm light

Generating 3 image variations...

  [1/3] ████████████████████ Complete
  [2/3] ████████████████████ Complete
  [3/3] ████████████████████ Complete

Images saved to: ~/Desktop/frconor-posts/2025-12-12/

  Image 1: hopper_shepherd_v1.png — Solitary figure by window, golden hour
  Image 2: hopper_shepherd_v2.png — Pastoral scene, figure in doorway
  Image 3: hopper_shepherd_v3.png — Interior with warm lamp, contemplative mood

───────────────────────────────────────────────────────────────────────

Enter image number (1-3), or:
  [r] Regenerate with same style
  [s] Switch to different art style
  [v] View images in Finder

Your choice: 2

✓ Selected: hopper_shepherd_v2.png

───────────────────────────────────────────────────────────────────────
  FINAL PREVIEW
───────────────────────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  [IMAGE: hopper_shepherd_v2.png]                                    │
│                                                                     │
│  The shepherd doesn't count the 99. He counts *you*.                │
│                                                                     │
│  Today's meditation: *The Good Shepherd*                            │
│                                                                     │
│  🎧 Apple: https://podcasts.apple.com/us/podcast/the-good-          │
│     shepherd/id1643273205?i=1000638229472                           │
│  Spotify: https://open.spotify.com/episode/5BA0ueDmbor2rs8Ps7vM53   │
│                                                                     │
│  📖 Transcript: https://tinyurl.com/frcmed-goodshepherd             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

───────────────────────────────────────────────────────────────────────

Approve this post?
  [y] Yes, finalize
  [e] Edit quote text
  [i] Choose different image
  [q] Start over

Your choice: y

───────────────────────────────────────────────────────────────────────
  ✓ POST READY
───────────────────────────────────────────────────────────────────────

✓ Image saved: ~/Desktop/frconor-posts/2025-12-12/final_post.png
✓ Post text copied to clipboard
✓ Logged to post history

TO POST ON WHATSAPP:
  1. Open WhatsApp Desktop or Web
  2. Go to "Fr. Conor Meditation Updates" channel
  3. Click attachment icon → Select image from Desktop
  4. Paste text (Cmd+V) in caption field
  5. Send!

═══════════════════════════════════════════════════════════════════════
```

---

## 4. Technical Architecture

### 4.1 System Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER'S MACHINE                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                   LLM OPTIONS (Quote Generation)              │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐              │  │
│  │  │  Gemini    │  │   Codex    │  │   Claude   │              │  │
│  │  │  CLI       │  │   CLI      │  │   Code     │              │  │
│  │  │ (default)  │  │            │  │            │              │  │
│  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘              │  │
│  │        └───────────────┼───────────────┘                      │  │
│  │                        ▼                                      │  │
│  └────────────────────────┼─────────────────────────────────────┘  │
│                           │                                        │
│                           ▼                                        │
│                  ┌────────────────┐    ┌──────────────────────┐   │
│                  │  Main Script   │───▶│  nano-banana MCP     │   │
│                  │  (Python)      │    │  (Image Generation)  │   │
│                  └──────┬─────────┘    └──────────────────────┘   │
│                         │                                          │
│                         ▼                                          │
│                ┌────────────────┐                                  │
│                │  Config Files  │                                  │
│                │  - settings.json (LLM choice)                     │
│                │  - styles.json                                    │
│                │  - prompts/                                       │
│                │  - state.json                                     │
│                └────────────────┘                                  │
│                         │                                          │
│                         ▼                                          │
│                ┌────────────────┐                                  │
│                │    Outputs     │                                  │
│                │  - Images (Desktop)                               │
│                │  - Clipboard                                      │
│                │  - History log                                    │
│                └────────────────┘                                  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SERVICES                             │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────────┐    ┌──────────────────────────────────┐ │
│  │  GitHub Pages        │    │  Google Gemini API               │ │
│  │  (Transcript fetch)  │    │  (via Gemini CLI & nano-banana)  │ │
│  │  frconor-ebook.      │    │  - Quote generation (optional)   │ │
│  │  github.io           │    │  - Image generation              │ │
│  └──────────────────────┘    └──────────────────────────────────┘ │
│                                                                    │
│  ┌──────────────────────┐    ┌──────────────────────────────────┐ │
│  │  OpenAI API          │    │  Anthropic API                   │ │
│  │  (via Codex CLI)     │    │  (via Claude Code CLI)           │ │
│  │  - Quote generation  │    │  - Quote generation              │ │
│  └──────────────────────┘    └──────────────────────────────────┘ │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### 4.2 Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Runtime | Claude Code CLI / Codex CLI / Gemini CLI | Multiple options, user preference |
| Quote Generation | Gemini CLI, Codex CLI, or Claude | Flexibility, best model for creative writing |
| Image Generation | nano-banana MCP Server | Already configured, uses Gemini |
| Transcript Fetch | HTTP GET (requests/httpx) | Simple, no auth needed |
| URL Shortener | `frcmed_shorten_cli.py` | Custom TinyURL aliases for transcript links |
| Clipboard | `pyperclip` or native `pbcopy` | Cross-platform clipboard access |
| Config Storage | JSON files | Simple, human-readable, git-trackable |
| Image Output | PNG files to Desktop | Easy drag-and-drop to WhatsApp |

### 4.3 LLM Options for Quote Generation

The system supports multiple LLMs for quote generation. Configure your preferred option in `settings.json`:

| LLM | Command | Pros | Cons |
|-----|---------|------|------|
| **Gemini 3 Pro** (Recommended) | `gemini "prompt" --model gemini-3-pro-preview` | Excellent creative writing, fast | Requires Gemini CLI setup |
| **Codex CLI** | `codex exec "prompt"` | OpenAI models, good at following structure | Requires OpenAI API key |
| **Claude Code** | `claude -p "prompt"` | Native MCP support, consistent | May be slower |

**Gemini CLI Usage:**
```bash
# Basic quote generation
gemini "Generate 15 hooks for meditation titled 'The Good Shepherd'" --model gemini-3-pro-preview

# With system prompt from file
gemini --system-prompt prompts/quote_generation.md "Episode: The Good Shepherd. Transcript: ..." --model gemini-3-pro-preview
```

**Codex CLI Usage:**
```bash
# Non-interactive execution
codex exec "Generate 15 hooks for meditation titled 'The Good Shepherd' using these styles..."

# With full auto mode
codex --full-auto "Generate meditation hooks based on this transcript..."
```

**Claude Code Usage:**
```bash
# Interactive mode
claude -p "Generate 15 hooks for meditation..."

# With image context (if needed)
claude -p "Generate hooks" -i transcript_screenshot.png
```

### 4.4 Dependencies

```
# Python packages (if using Python script)
requests>=2.28.0      # HTTP client for fetching transcripts
beautifulsoup4>=4.12  # HTML parsing for transcript extraction
pyperclip>=1.8.0      # Clipboard operations (optional, can use pbcopy)

# CLI Tools (at least one required for quote generation)
gemini                # Google Gemini CLI (recommended for quotes)
codex                 # OpenAI Codex CLI (alternative)
claude                # Anthropic Claude Code CLI

# URL Shortener (required)
# Located at: /Users/e_wijaya_ap/Desktop/upload_frcmed_to_web/meditations/preprocessing_scripts/frcmed_shorten_cli.py
python frcmed_shorten_cli.py <url>  # Creates custom TinyURL aliases

# MCP Servers (already configured)
nano-banana MCP       # Image generation via Gemini
```

### 4.5 CLI Tool Installation

**Gemini CLI:**
```bash
# Install via pip
pip install google-generativeai

# Or if using the standalone CLI
# Follow: https://github.com/google-gemini/gemini-cli

# Authenticate
gemini login
```

**Codex CLI:**
```bash
# Install Codex CLI (OpenAI)
npm install -g @openai/codex

# Or via the official installer
# Configure with OpenAI API key
codex login
```

**Claude Code CLI:**
```bash
# Already installed per user confirmation
# Verify with:
claude --version
```

---

## 5. Detailed Requirements

### 5.1 URL Input Module

**REQ-INPUT-001: URL Collection**
- System MUST prompt for exactly 3 URLs in order:
  1. Apple Podcasts URL
  2. Spotify URL
  3. Transcript URL
- System MUST validate URL format before proceeding
- System SHOULD accept URLs with or without trailing parameters

**REQ-INPUT-002: Title Extraction**
- System MUST extract episode title from Apple Podcasts URL
- URL pattern: `https://podcasts.apple.com/us/podcast/{title-slug}/id1643273205?i={episode-id}`
- Extract `{title-slug}`, convert hyphens to spaces, apply title case
- Example: `the-good-shepherd` → "The Good Shepherd"

**REQ-INPUT-003: URL Validation**

| URL Type | Required Pattern | Validation |
|----------|------------------|------------|
| Apple Podcasts | `podcasts.apple.com/*/podcast/*` | Contains `id1643273205` |
| Spotify | `open.spotify.com/episode/*` | Valid Spotify episode URL |
| Transcript | `frconor-ebook.github.io/meditations/homilies/*` | Ends with `/` |

### 5.2 Transcript Fetching Module

**REQ-FETCH-001: HTTP Retrieval**
- System MUST fetch transcript via HTTP GET request
- System MUST handle network errors gracefully with retry (max 3 attempts)
- System MUST timeout after 30 seconds

**REQ-FETCH-002: Content Extraction**
- Transcript pages are HTML with meditation text in `<article>` or main content area
- System MUST extract plain text content, stripping HTML tags
- System MUST preserve paragraph structure for context
- System SHOULD extract between 500-5000 words of content

**REQ-FETCH-003: Error Handling**

| Error | Behavior |
|-------|----------|
| 404 Not Found | Display error, prompt user to verify URL |
| Network timeout | Retry up to 3 times, then fail gracefully |
| Empty content | Display warning, allow user to proceed or retry |

### 5.3 Quote Generation Module

**REQ-QUOTE-001: LLM Selection**
- System MUST support multiple LLMs for quote generation
- Default LLM configurable in `settings.json`
- Supported LLMs:
  - `gemini` - Google Gemini 3 Pro Preview (recommended)
  - `codex` - OpenAI Codex CLI
  - `claude` - Anthropic Claude Code CLI

**REQ-QUOTE-002: Generation Volume**
- System MUST generate exactly 15 hook options per session
- Breakdown:
  - 5 hooks using defined creative styles (1 per style)
  - 5 hooks that are poignant/emotionally devastating
  - 5 hooks with varied tones and angles

**REQ-QUOTE-003: LLM Invocation**

**Gemini CLI (Recommended):**
```bash
gemini "$(cat <<EOF
Episode Title: {episode_title}
Transcript excerpt: {transcript_excerpt}

Generate exactly 15 hooks following these styles:
[... full prompt from prompts/quote_generation.md ...]
EOF
)" --model gemini-3-pro-preview
```

**Codex CLI:**
```bash
codex exec "$(cat <<EOF
Episode Title: {episode_title}
Transcript excerpt: {transcript_excerpt}

Generate exactly 15 hooks following these styles:
[... full prompt from prompts/quote_generation.md ...]
EOF
)"
```

**Claude Code CLI:**
```bash
claude -p "$(cat <<EOF
Episode Title: {episode_title}
Transcript excerpt: {transcript_excerpt}

Generate exactly 15 hooks following these styles:
[... full prompt from prompts/quote_generation.md ...]
EOF
)"
```

**REQ-QUOTE-005: Creative Styles**

| # | Style Name | Rhetorical Devices | Example |
|---|------------|-------------------|---------|
| 1 | Provocative Question | Antithesis, Paradox | "Why does the path to *connection* require _solitude_?" |
| 2 | Minimalist Moment | Scesis Onomaton, Diacope | "Peace. _Real_ peace. It's closer than you think." |
| 3 | Witty Reframe | Catachresis, Paradox | "Today, let's listen to the _shape of silence_." |
| 4 | Direct Invitation | Isocolon, Alliteration | "Let go of what was. _Welcome what is_." |
| 5 | Profound Tease | Chiasmus, Fourteenth Rule | "Stop trying to _find_ the path. Let it find *you*." |

**REQ-QUOTE-006: Formatting Requirements**
- Maximum 3-4 lines total per hook
- Use `*asterisks*` for bold emphasis
- Use `_underscores_` for italic emphasis
- Matching pairs only (no unclosed formatting)
- Avoid clichés at all costs

**REQ-QUOTE-007: User Selection**
- Display all 15 hooks with clear numbering and style labels
- User enters number to select
- `r` = regenerate all hooks
- `m` = modify specific hook (prompt for number, then new version)

### 5.4 Image Generation Module

**REQ-IMAGE-001: Art Style Rotation**
- System MUST maintain a rotation queue of art styles
- System MUST track current position in rotation (persisted to state file)
- System MUST advance to next style after each successful post
- Rotation queue (see Section 6.2 for full definitions):
  1. Frederick William Elwell
  2. John French Sloan (Ashcan School)
  3. Edward Hopper
  4. Joaquín Sorolla
  5. Andrew Wyeth
  6. Winslow Homer (Watercolor)
  7. Kawase Hasui (Shin Hanga)
  8. Vermeer

**REQ-IMAGE-002: Image Generation**
- System MUST generate exactly 3 image variations per request
- System MUST use nano-banana MCP's `generate_image` function
- Recommended parameters:
  ```python
  generate_image(
      prompt=<constructed_prompt>,
      model_tier="pro",        # Use Pro for quality
      resolution="high",       # High resolution
      aspect_ratio="4:3",      # Good for social media
      n=3                      # Generate 3 variations
  )
  ```

**REQ-IMAGE-003: Prompt Construction**
- Image prompt MUST incorporate:
  - Selected quote's theme and mood
  - Current art style's characteristics
  - Compositional requirements (rule of thirds, negative space for text)
  - Cultural sensibility appropriate to the style
- See Section 7.2 for full prompt template

**REQ-IMAGE-004: Retry Logic**

| Failure | Action |
|---------|--------|
| Generation fails (API error) | Retry same prompt up to 2 times |
| All retries fail | Switch to next art style in rotation, retry |
| 2 styles fail | Display error, allow manual prompt entry |

**REQ-IMAGE-005: User Selection**
- Display 3 image thumbnails or file paths
- Options:
  - `1/2/3` = select image
  - `r` = regenerate with same style
  - `s` = switch to different style (show list)
  - `v` = open images in Finder/file browser

### 5.6 URL Shortening Module

**REQ-SHORTEN-001: Transcript URL Shortening**
- System MUST shorten the transcript URL before composing final post
- System MUST use the custom `frcmed_shorten_cli.py` script
- Shortened URLs use TinyURL with custom aliases

**REQ-SHORTEN-002: Script Invocation**
```bash
python /Users/e_wijaya_ap/Desktop/upload_frcmed_to_web/meditations/preprocessing_scripts/frcmed_shorten_cli.py \
  "https://frconor-ebook.github.io/meditations/homilies/the-good-shepherd/"
```

**REQ-SHORTEN-003: Expected Output**
- Input: `https://frconor-ebook.github.io/meditations/homilies/the-good-shepherd/`
- Output: `https://tinyurl.com/frcmed-goodshepherd` (or similar custom alias)

**REQ-SHORTEN-004: Error Handling**

| Error | Behavior |
|-------|----------|
| Script not found | Display warning, use original URL |
| TinyURL API failure | Retry once, then use original URL with warning |
| Network timeout | Use original URL, notify user |

**REQ-SHORTEN-005: Caching (Optional)**
- System MAY cache shortened URLs to avoid redundant API calls
- Cache location: `~/.frconor-automation/cache/shortened_urls.json`

### 5.7 Post Composition Module

**REQ-COMPOSE-001: Post Format**
```
{hook_text}

Today's meditation: *{episode_title}*

🎧 Apple: {apple_url}
Spotify: {spotify_url}

📖 Transcript: {shortened_transcript_url}
```

Note: The transcript URL MUST be shortened using `frcmed_shorten_cli.py` before inclusion.

**REQ-COMPOSE-002: Character Limits**
- Hook text: Maximum 280 characters (WhatsApp-friendly)
- Total post: Should fit comfortably in WhatsApp caption

**REQ-COMPOSE-003: Preview Display**
- Show formatted post with visual box/border
- Show selected image filename
- Show character count

**REQ-COMPOSE-004: Edit Capability**
- User can edit hook text inline
- User can switch to different image
- User can restart entire flow

### 5.8 Output Module

**REQ-OUTPUT-001: Image File Output**
- Save final selected image to: `~/Desktop/frconor-posts/{YYYY-MM-DD}/final_post.png`
- Create directory if it doesn't exist
- Also save all generated variations for reference

**REQ-OUTPUT-002: Clipboard Copy**
- Copy final post text (without image) to system clipboard
- Use `pbcopy` on macOS or `pyperclip` library
- Confirm copy with message

**REQ-OUTPUT-003: History Logging**
- Append entry to `~/.frconor-automation/post_history.json`
- Entry schema:
  ```json
  {
    "date": "2025-12-12",
    "title": "The Good Shepherd",
    "hook": "The shepherd doesn't count the 99...",
    "style": "Edward Hopper",
    "apple_url": "...",
    "spotify_url": "...",
    "transcript_url": "...",
    "image_path": "..."
  }
  ```

**REQ-OUTPUT-004: Success Message**
- Display clear instructions for manual WhatsApp posting
- Show file location for image
- Confirm clipboard content

---

## 6. Data Models & Configuration

### 6.1 Settings File (`settings.json`)

```json
{
  "llm": {
    "quote_generation": {
      "provider": "gemini",
      "model": "gemini-3-pro-preview",
      "fallback_provider": "claude"
    },
    "providers": {
      "gemini": {
        "command": "gemini",
        "model_flag": "--model",
        "default_model": "gemini-3-pro-preview"
      },
      "codex": {
        "command": "codex",
        "subcommand": "exec",
        "default_model": null
      },
      "claude": {
        "command": "claude",
        "prompt_flag": "-p",
        "default_model": null
      }
    }
  },
  "url_shortener": {
    "script_path": "/Users/e_wijaya_ap/Desktop/upload_frcmed_to_web/meditations/preprocessing_scripts/frcmed_shorten_cli.py",
    "enabled": true,
    "cache_enabled": true
  },
  "output": {
    "image_directory": "~/Desktop/frconor-posts",
    "copy_to_clipboard": true,
    "open_finder_after_generation": true
  },
  "image_generation": {
    "variations_count": 3,
    "model_tier": "pro",
    "resolution": "high",
    "aspect_ratio": "4:3",
    "retry_attempts": 2
  }
}
```

### 6.2 State File (`state.json`)

```json
{
  "style_rotation_index": 3,
  "last_post_date": "2025-12-11",
  "total_posts": 147
}
```

### 6.3 Art Styles Configuration (`art_styles.json`)

```json
{
  "rotation": [
    {
      "id": "elwell",
      "name": "Frederick William Elwell",
      "period": "Victorian/Edwardian",
      "cultural_fit": ["British", "European", "domestic"],
      "mood_keywords": ["warm", "domestic", "contemplative", "intimate"],
      "prompt_elements": {
        "style_description": "in the style of Frederick William Elwell, Victorian-era British painter known for warm domestic interiors and intimate scenes",
        "color_palette": "warm earth tones, soft natural light through windows, muted golds and browns",
        "composition": "intimate interior scenes, figures engaged in quiet activity, soft chiaroscuro",
        "avoid": "modern elements, harsh lighting, abstract forms"
      }
    },
    {
      "id": "sloan",
      "name": "John French Sloan (Ashcan School)",
      "period": "Early 20th Century American",
      "cultural_fit": ["American", "urban", "working class"],
      "mood_keywords": ["everyday life", "candid", "social realism", "authentic"],
      "prompt_elements": {
        "style_description": "in the style of John Sloan, Ashcan School painter capturing urban American life with warmth and authenticity",
        "color_palette": "urban grays and browns with warm accent colors, gaslight ambiance",
        "composition": "street scenes, rooftop views, ordinary people in daily activities",
        "avoid": "idealized beauty, rural settings, aristocratic subjects"
      }
    },
    {
      "id": "hopper",
      "name": "Edward Hopper",
      "period": "20th Century American Realism",
      "cultural_fit": ["American", "urban", "solitary"],
      "mood_keywords": ["solitude", "contemplation", "isolation", "light and shadow"],
      "prompt_elements": {
        "style_description": "in the style of Edward Hopper, American realist known for dramatic light and contemplative solitude",
        "color_palette": "stark contrasts, warm interior light against cool shadows, muted urban colors",
        "composition": "single figures in architectural spaces, strong geometric shapes, dramatic window light",
        "avoid": "crowds, busy scenes, pastoral settings"
      }
    },
    {
      "id": "sorolla",
      "name": "Joaquín Sorolla",
      "period": "Spanish Impressionism",
      "cultural_fit": ["Mediterranean", "Spanish", "coastal"],
      "mood_keywords": ["luminous", "joyful", "sunlit", "beach scenes"],
      "prompt_elements": {
        "style_description": "in the style of Joaquín Sorolla, Spanish master of light capturing Mediterranean brilliance",
        "color_palette": "brilliant whites, sun-drenched colors, azure blues, warm skin tones",
        "composition": "figures in bright sunlight, beach and garden scenes, flowing white fabrics",
        "avoid": "dark interiors, northern European settings, somber moods"
      }
    },
    {
      "id": "wyeth",
      "name": "Andrew Wyeth",
      "period": "20th Century American Regionalism",
      "cultural_fit": ["American", "rural", "New England"],
      "mood_keywords": ["melancholy", "stark", "introspective", "rural America"],
      "prompt_elements": {
        "style_description": "in the style of Andrew Wyeth, American painter of stark rural landscapes and introspective figures",
        "color_palette": "muted earth tones, dry grass browns, weathered grays, pale winter light",
        "composition": "isolated figures in vast landscapes, weathered buildings, detailed textures",
        "avoid": "urban settings, bright colors, joyful crowds"
      }
    },
    {
      "id": "homer",
      "name": "Winslow Homer (Watercolor)",
      "period": "American Realism",
      "cultural_fit": ["American", "maritime", "nature"],
      "mood_keywords": ["sea", "struggle", "nature", "atmospheric"],
      "prompt_elements": {
        "style_description": "in the watercolor style of Winslow Homer, capturing the drama of sea and nature with fluid brushwork",
        "color_palette": "ocean blues and greens, storm grays, tropical watercolor washes",
        "composition": "figures against sea or sky, dynamic weather, boats and coastlines",
        "avoid": "urban scenes, dry inland settings, heavy oil painting texture"
      }
    },
    {
      "id": "hasui",
      "name": "Kawase Hasui (Shin Hanga)",
      "period": "20th Century Japanese",
      "cultural_fit": ["Japanese", "Asian", "seasonal"],
      "mood_keywords": ["serene", "seasonal", "poetic", "traditional"],
      "prompt_elements": {
        "style_description": "in the Shin Hanga style of Kawase Hasui, Japanese woodblock print master of atmospheric landscapes",
        "color_palette": "subtle gradients, rain and snow effects, twilight blues and grays, cherry blossom pinks",
        "composition": "landscapes with architectural elements, seasonal atmosphere, reflections in water",
        "avoid": "Western architecture, harsh contrasts, non-Japanese settings"
      }
    },
    {
      "id": "vermeer",
      "name": "Johannes Vermeer",
      "period": "Dutch Golden Age",
      "cultural_fit": ["Dutch", "European", "domestic"],
      "mood_keywords": ["intimate", "luminous", "quiet", "domestic"],
      "prompt_elements": {
        "style_description": "in the style of Johannes Vermeer, Dutch master of light and intimate domestic scenes",
        "color_palette": "Vermeer blue and yellow, soft diffused daylight, pearl-like luminosity",
        "composition": "single figure by window, domestic interiors, maps and letters, characteristic left-side lighting",
        "avoid": "outdoor scenes, multiple figures, dark or dramatic lighting"
      }
    }
  ]
}
```

### 6.4 Post History Schema (`post_history.json`)

```json
{
  "posts": [
    {
      "id": "2025-12-12-001",
      "created_at": "2025-12-12T18:37:00Z",
      "episode": {
        "title": "The Good Shepherd",
        "apple_url": "https://podcasts.apple.com/...",
        "spotify_url": "https://open.spotify.com/...",
        "transcript_url": "https://frconor-ebook.github.io/...",
        "transcript_url_shortened": "https://tinyurl.com/frcmed-goodshepherd"
      },
      "content": {
        "hook": "The shepherd doesn't count the 99. He counts *you*.",
        "hook_style": "Poignant",
        "full_post_text": "..."
      },
      "image": {
        "style": "Edward Hopper",
        "style_id": "hopper",
        "file_path": "~/Desktop/frconor-posts/2025-12-12/final_post.png",
        "prompt_used": "..."
      }
    }
  ]
}
```

---

## 7. Prompts & Templates

### 7.1 Quote Generation Prompt

This is the master prompt used to generate the 15 hooks. Store in `prompts/quote_generation.md`:

```markdown
# Fr. Conor Meditation Hook Generator

You are generating WhatsApp post hooks for "Fr. Conor Meditation Updates" channel.

## Input Context
- Episode Title: {episode_title}
- Transcript excerpt (key passages): {transcript_excerpt}

## Output Requirements
Generate exactly 15 hooks following this structure:

### SECTION 1: Creative Styles (5 hooks, one per style)

**Style 1 — Provocative Question (use Antithesis or Paradox)**
Goal: Open with a question highlighting tension or surprising truth.
- Antithesis example: "Why does the path to *connection* require _solitude_?"
- Paradox example: "What if the greatest strength is found in _weakness_?"

**Style 2 — Minimalist Moment (use Scesis Onomaton or Diacope)**
Goal: Short, impactful anchor for a busy person.
- Scesis Onomaton (no main verb): "A quiet mind. A calm heart. A moment just for *you*."
- Diacope (word repetition): "Peace. _Real_ peace. It's closer than you think."

**Style 3 — Witty Reframe (use Catachresis or Paradox)**
Goal: Playful metaphor or startling observation.
- Catachresis (creative misuse): "Today, let's listen to the _shape of silence_."
- Witty Paradox: "The funny thing about shortcuts is they take the *long way*."

**Style 4 — Direct Invitation (use Isocolon or Alliteration)**
Goal: Warm, balanced invitation.
- Isocolon (parallel clauses): "Let go of what was. _Welcome what is_."
- Alliteration: "Finding *peace and purpose* in the pause."

**Style 5 — Profound Tease (use Chiasmus or Fourteenth Rule)**
Goal: Hint at deep insight that promises transformation.
- Chiasmus (reversal): "Stop trying to _find_ the path. Let the path find *you*."
- Fourteenth Rule (specific number): "There are *three words* that can disarm any fear."

### SECTION 2: Poignant & Emotionally Devastating (5 hooks)
These should touch on pain, loss, longing, or deep human struggle.
- Aim for hooks that might make someone pause and feel something profound
- Can reference: loneliness, searching, brokenness, being lost, grief, longing for home
- Should feel deeply human while pointing toward hope

### SECTION 3: Varied Tones (5 hooks)
Mix of approaches not covered above:
- Gentle encouragement
- Bold declaration
- Quiet observation
- Unexpected angle
- Simple truth

## Formatting Rules
- Maximum 3-4 lines per hook
- Use `*asterisks*` for bold, `_underscores_` for italic
- Always use matching pairs
- AVOID clichés: "journey", "embrace", "unlock", "discover your potential"
- Each hook must stand alone without context
- Warm, conversational tone

## Output Format
Return as numbered list (1-15) with style labels for first 10:

1. [Provocative Question]: "..."
2. [Provocative Question alt]: "..."
3. [Minimalist Moment]: "..."
... etc
```

### 7.2 Image Generation Prompt Template

Template for constructing the image generation prompt. Store in `prompts/image_generation.md`:

```markdown
# Image Prompt Template

## Variables
- {quote}: The selected hook text
- {style}: Art style object from art_styles.json
- {themes}: Extracted themes from transcript

## Prompt Structure

Create an image {style.prompt_elements.style_description}.

**Scene Requirements:**
- The scene should visually evoke the feeling of: "{quote}"
- Key themes to incorporate: {themes}
- Cultural context: {style.cultural_fit}
- Emotional mood: {style.mood_keywords}

**Visual Specifications:**
- Color palette: {style.prompt_elements.color_palette}
- Composition approach: {style.prompt_elements.composition}
- Must avoid: {style.prompt_elements.avoid}

**Technical Requirements:**
- Apply rule of thirds, position key elements along grid lines
- Leave negative space in upper-right area for text overlay (optional)
- 1-3 human figures maximum as primary subjects
- No text, watermarks, or signatures in the image
- Secular scene only (no explicitly religious iconography)

**Aspect Ratio:** 4:3 (landscape, suitable for social media)
```

### 7.3 Example Constructed Image Prompt

For quote "The shepherd doesn't count the 99. He counts *you*." with Edward Hopper style:

```
Create an image in the style of Edward Hopper, American realist known for
dramatic light and contemplative solitude.

Scene: A solitary figure sitting by a large window in late afternoon light.
The figure appears to be in quiet reflection, perhaps looking outward. The
scene evokes the feeling of being individually seen and known—the profound
intimacy of being counted, not as part of a crowd, but as oneself.

Visual Specifications:
- Color palette: stark contrasts, warm interior light against cool shadows,
  muted urban colors
- Composition: single figure in architectural space, strong geometric shapes,
  dramatic window light from the left
- Avoid: crowds, busy scenes, pastoral settings, explicit religious imagery

Technical Requirements:
- Apply rule of thirds
- Leave negative space in upper portion
- 1 human figure as primary subject
- No text or signatures

Aspect Ratio: 4:3
```

---

## 8. File Structure

```
~/.frconor-automation/
├── config/
│   ├── art_styles.json          # Art style definitions and rotation queue
│   └── settings.json            # User preferences (LLM choice, output paths, etc.)
│
├── prompts/
│   ├── quote_generation.md      # Master prompt for hook generation
│   └── image_generation.md      # Template for image prompts
│
├── state/
│   ├── state.json               # Current rotation index, last post date
│   └── post_history.json        # Log of all posts
│
├── cache/
│   ├── transcripts/             # Cached transcript files (optional)
│   └── shortened_urls.json      # Cache of shortened URLs to avoid redundant API calls
│
└── logs/
    └── automation.log           # Debug logs (optional)

~/Desktop/frconor-posts/
├── 2025-12-11/
│   ├── variation_1.png
│   ├── variation_2.png
│   ├── variation_3.png
│   └── final_post.png
│
└── 2025-12-12/
    ├── variation_1.png
    ├── variation_2.png
    ├── variation_3.png
    └── final_post.png

# External dependency (already exists)
/Users/e_wijaya_ap/Desktop/upload_frcmed_to_web/meditations/preprocessing_scripts/
└── frcmed_shorten_cli.py        # URL shortener script
```

### 8.1 Configuration Priority

When loading settings, the system checks in this order:
1. Command-line flags (highest priority)
2. Environment variables (`FRCONOR_LLM_PROVIDER`, `FRCONOR_OUTPUT_DIR`)
3. `~/.frconor-automation/config/settings.json`
4. Built-in defaults (lowest priority)

---

## 9. Implementation Phases

### Phase 1: Core Pipeline (Week 1)
**Goal:** Basic end-to-end flow working

- [ ] URL input collection and validation
- [ ] Title extraction from Apple URL
- [ ] Transcript fetching (basic HTTP GET)
- [ ] Quote generation with Claude (simplified: 5 hooks only)
- [ ] User selection for quotes
- [ ] Basic image generation via nano-banana MCP (1 image)
- [ ] Output to clipboard and file

**Deliverable:** Can run tool and get one hook + one image

### Phase 2: Full Quote System (Week 2)
**Goal:** Complete 15-hook generation with all styles

- [ ] Implement all 5 creative styles
- [ ] Add poignant and varied sections
- [ ] Quote formatting validation
- [ ] Regeneration option
- [ ] Modify specific hook option

**Deliverable:** Full 15 hooks displayed with proper formatting

### Phase 3: Image System (Week 3)
**Goal:** Complete image generation with rotation

- [ ] Art styles configuration file
- [ ] Style rotation state management
- [ ] Generate 3 variations per request
- [ ] Retry logic with style fallback
- [ ] User selection interface (1/2/3/r/s/v)
- [ ] Image prompt construction using templates

**Deliverable:** 3 images generated per session, rotation works

### Phase 4: Polish & Edge Cases (Week 4)
**Goal:** Production-ready tool

- [ ] Post history logging
- [ ] Comprehensive error handling
- [ ] Network timeout and retry
- [ ] Input validation edge cases
- [ ] Clear error messages
- [ ] Help command (`--help`)
- [ ] View history command (`--history`)

**Deliverable:** Robust tool ready for daily use

---

## 10. Testing Criteria

### 10.1 Unit Tests

| Test | Input | Expected Output |
|------|-------|-----------------|
| Title extraction | `podcasts.apple.com/.../the-good-shepherd/...` | "The Good Shepherd" |
| Title extraction (hyphenated) | `our-sins-our-confession` | "Our Sins, Our Confession" |
| URL validation (valid Apple) | `https://podcasts.apple.com/us/podcast/x/id1643273205?i=123` | `True` |
| URL validation (invalid) | `https://youtube.com/watch?v=123` | `False` |
| Style rotation (wrap) | index=7, advance | index=0 |
| Hook formatting | `*bold* and _italic_` | Valid (matching pairs) |
| Hook formatting | `*bold and _italic_` | Invalid (mismatched) |
| URL shortening | `https://frconor-ebook.github.io/meditations/homilies/the-good-shepherd/` | `https://tinyurl.com/frcmed-*` |
| URL shortening (script not found) | Invalid script path | Returns original URL + warning |

### 10.2 Integration Tests

| Test | Steps | Expected Result |
|------|-------|-----------------|
| Full pipeline | Provide 3 valid URLs | Generates hooks, images, outputs file |
| Network failure | Invalid transcript URL | Graceful error, retry prompt |
| Image failure | Force nano-banana error | Retries, falls back to next style |
| State persistence | Run twice, check rotation | Second run uses next style |

### 10.3 Manual Testing Checklist

- [ ] Run with real meditation URLs
- [ ] Verify all 15 hooks display correctly
- [ ] Select hook, verify selection confirmed
- [ ] Verify 3 images generated
- [ ] Open images in Finder
- [ ] Select image, verify final preview
- [ ] **Verify transcript URL is shortened (tinyurl.com/frcmed-*)**
- [ ] Approve, verify clipboard content contains shortened URL
- [ ] Verify image saved to Desktop
- [ ] Verify history entry created with both original and shortened URLs
- [ ] Run again, verify rotation advanced
- [ ] Test regeneration options
- [ ] Test style switching
- [ ] Test on slow network
- [ ] **Test with URL shortener disabled (should use original URL)**
- [ ] **Test with invalid shortener script path (should gracefully fallback)**

---

## 11. Appendices

### Appendix A: WhatsApp Channel Info

- **Channel Name:** Fr. Conor Meditation Updates
- **Channel URL:** https://whatsapp.com/channel/0029Vb2pjJyGufJ2mE4xvv2F
- **Posting Method:** Manual (WhatsApp Desktop/Web)
- **Best Posting Time:** Evening (6-7 PM local time)

### Appendix B: Source URLs

- **Podcast (Apple):** https://podcasts.apple.com/us/podcast/fr-conor-donnelly-meditations/id1643273205
- **Podcast (Spotify):** https://open.spotify.com/show/0cMxJXlWg6QJD7t8LAYM7v
- **Transcripts:** https://frconor-ebook.github.io/meditations/

### Appendix C: LLM CLI Reference

**Gemini CLI (Recommended for Quote Generation):**
```bash
# Basic usage
gemini "Your prompt here" --model gemini-3-pro-preview

# With system instructions
gemini --system-prompt "You are a creative writer..." "Generate hooks" --model gemini-3-pro-preview

# List available models
gemini models

# Check authentication
gemini login
```

**Codex CLI (OpenAI):**
```bash
# Non-interactive execution
codex exec "Your prompt here"

# With specific model
codex exec -m gpt-4 "Your prompt here"

# Full auto mode (no confirmations)
codex --full-auto "Your prompt here"

# With custom working directory
codex -C /path/to/dir "Your prompt here"

# With image attachment
codex exec -i image.png "Describe this"
```

**Claude Code CLI:**
```bash
# Basic prompt
claude -p "Your prompt here"

# With image
claude -p "Describe this image" -i image.png

# With specific model
claude -m claude-sonnet-4-20250514 -p "Your prompt"
```

### Appendix D: nano-banana MCP Reference

**Installation:** Already configured in Claude Code

**Key Function:**
```python
generate_image(
    prompt: str,              # The image description
    model_tier: str = "auto", # "flash", "pro", or "auto"
    resolution: str = "high", # "standard", "high", or "4k" (pro only)
    aspect_ratio: str = "4:3", # "1:1", "4:3", "16:9", "9:16", etc.
    n: int = 1                # Number of images (1-4)
)
```

**Output:** Images saved to `~/nanobanana-images/` by default

### Appendix E: Sample Transcript Structure

Transcripts at `frconor-ebook.github.io` follow this HTML structure:

```html
<article>
  <h1>Episode Title</h1>
  <p>Meditation text paragraph 1...</p>
  <p>Meditation text paragraph 2...</p>
  <!-- Closing prayer at the end -->
  <p>I thank you, my God, for the good resolutions...</p>
</article>
```

Key extraction points:
- Main content is in `<article>` or `<main>` tag
- Paragraphs are `<p>` tags
- Skip the closing prayer (last paragraph starting with "I thank you")
- Extract ~2000-4000 words for analysis

### Appendix F: URL Shortener Reference

**Script Location:**
```
/Users/e_wijaya_ap/Desktop/upload_frcmed_to_web/meditations/preprocessing_scripts/frcmed_shorten_cli.py
```

**Usage:**
```bash
# Basic usage (copies to clipboard by default)
python frcmed_shorten_cli.py "https://frconor-ebook.github.io/meditations/homilies/the-good-shepherd/"

# Multiple URLs
python frcmed_shorten_cli.py "url1" "url2" "url3"

# Disable clipboard copy
python frcmed_shorten_cli.py --no-copy "https://frconor-ebook.github.io/..."
```

**Output:**
- Creates custom TinyURL alias based on episode slug
- Example: `the-good-shepherd` → `https://tinyurl.com/frcmed-goodshepherd`

**Integration in Main Script:**
```python
import subprocess

def shorten_transcript_url(url: str, settings: dict) -> str:
    """Shorten transcript URL using frcmed_shorten_cli.py"""
    script_path = settings.get("url_shortener", {}).get("script_path")

    if not script_path or not settings.get("url_shortener", {}).get("enabled", True):
        return url  # Return original if disabled

    try:
        result = subprocess.run(
            ["python", script_path, "--no-copy", url],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"Warning: URL shortening failed, using original URL")
            return url
    except Exception as e:
        print(f"Warning: URL shortener error: {e}")
        return url
```

### Appendix G: Rhetorical Device Reference

| Device | Definition | Example |
|--------|------------|---------|
| **Antithesis** | Contrasting ideas in parallel structure | "It was the best of times, it was the worst of times" |
| **Paradox** | Seemingly contradictory statement with truth | "Less is more" |
| **Scesis Onomaton** | Sentence without main verb | "A day of rest. A time of peace." |
| **Diacope** | Repetition with intervening words | "Bond. James Bond." |
| **Catachresis** | Creative/unusual use of a word | "I will speak daggers to her" |
| **Isocolon** | Parallel grammatical structure | "Veni, vidi, vici" |
| **Alliteration** | Repeated initial consonant sounds | "Peter Piper picked..." |
| **Chiasmus** | ABBA reversal structure | "Ask not what your country can do for you..." |
| **Fourteenth Rule** | Specific numbers create intrigue | "There are only 3 things that matter..." |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-12 | Product Owner | Initial PRD |

---

**END OF DOCUMENT**
```
