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
