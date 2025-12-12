# Image Concept Generator

You are generating visual scene concepts for meditation app images.

## Input
- Quote to visualize: "{quote}"
- Themes from meditation: {themes}
- Art style: {style_name}
- Style description: {style_description}
- Color palette: {color_palette}
- Composition approach: {composition}

## Task
Generate exactly 3 distinct visual scene concepts that could illustrate this quote.
Each concept should take a different interpretive approach while remaining suitable for the specified art style.

## Requirements for Each Concept
- Feature 1-3 human figures as primary subjects
- Evoke the emotional essence of the quote
- Be secular (no religious iconography)
- Be suitable for {style_name} artistic treatment
- Include specific, paintable visual details
- Match the mood and color palette of the style

## Output Format
Return exactly 3 concepts in this precise format:

1. [Setting Title]
   Scene: [2-3 sentences describing the visual scene in detail]
   Mood: [2-3 emotional tone words, comma-separated]
   Elements: [specific visual elements to include, comma-separated]

2. [Setting Title]
   Scene: [2-3 sentences describing the visual scene in detail]
   Mood: [2-3 emotional tone words, comma-separated]
   Elements: [specific visual elements to include, comma-separated]

3. [Setting Title]
   Scene: [2-3 sentences describing the visual scene in detail]
   Mood: [2-3 emotional tone words, comma-separated]
   Elements: [specific visual elements to include, comma-separated]
