# 4-Panel Comic Strip Concept Generator

You are generating 4-panel comic strip concepts for a meditation podcast visualization.

## Input
- Themes from meditation: {themes}
- Transcript excerpt: {transcript_excerpt}
- Comic art style: {style_name}
- Style description: {style_description}

## Task
Generate exactly 4 distinct 4-panel comic strip concepts that visualize key moments or teachings from this meditation.
Each concept should tell a complete mini-narrative across the 4 panels with natural dialogue.

## Comic Text Elements to Use
- **Speech Balloon** — spoken dialogue with a tail pointing to the speaker
- **Caption Box** — narrative text not spoken by characters (for scene-setting)
- **Thought Balloon** — cloud-like balloon for internal thoughts
- Keep dialogue SHORT and NATURAL — conversational, not poetic

## Panel Composition Requirements
- DENSE, RICH compositions — fill each panel with visual detail
- NO empty space or whitespace — every area should have something
- Include BACKGROUNDS with environmental details (furniture, plants, architecture, textures)
- Add secondary elements: objects on tables, items on walls, weather effects, lighting
- Characters should interact with their environment, not float in empty space

## Requirements for Each Concept
- Must work as a 4-panel horizontal strip (read left to right)
- Tell a complete narrative arc: setup → development → turn → resolution
- Feature 1-3 human figures as subjects (relatable, grounded in realistic settings)
- Include SHORT dialogue in each panel (speech, thought, or caption)
- Dialogue must be NATURAL and CONVERSATIONAL — no flowery or poetic language
- Be secular (no religious iconography)
- Be suitable for {style_name} artistic treatment
- Capture the emotional essence of the meditation themes

## Output Format
Return exactly 4 concepts in this precise format:

1. [Comic Title]
   Arc: [One sentence describing the narrative arc]
   Panel 1: [Scene description]
   Dialogue 1: [SPEECH: "dialogue" / THOUGHT: "thought" / CAPTION: "narration"]
   Panel 2: [Scene description]
   Dialogue 2: [Text type and content]
   Panel 3: [Scene description]
   Dialogue 3: [Text type and content]
   Panel 4: [Scene description]
   Dialogue 4: [Text type and content]

2. [Comic Title]
   Arc: [One sentence describing the narrative arc]
   Panel 1: [Scene description]
   Dialogue 1: [Text type and content]
   Panel 2: [Scene description]
   Dialogue 2: [Text type and content]
   Panel 3: [Scene description]
   Dialogue 3: [Text type and content]
   Panel 4: [Scene description]
   Dialogue 4: [Text type and content]

3. [Comic Title]
   Arc: [One sentence describing the narrative arc]
   Panel 1: [Scene description]
   Dialogue 1: [Text type and content]
   Panel 2: [Scene description]
   Dialogue 2: [Text type and content]
   Panel 3: [Scene description]
   Dialogue 3: [Text type and content]
   Panel 4: [Scene description]
   Dialogue 4: [Text type and content]

4. [Comic Title]
   Arc: [One sentence describing the narrative arc]
   Panel 1: [Scene description]
   Dialogue 1: [Text type and content]
   Panel 2: [Scene description]
   Dialogue 2: [Text type and content]
   Panel 3: [Scene description]
   Dialogue 3: [Text type and content]
   Panel 4: [Scene description]
   Dialogue 4: [Text type and content]
