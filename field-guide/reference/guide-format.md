# Field guide format

Every guide is one JSON content file (`guides/<slug>.json`). The design lives only in
`template.html`. `build.py` checks the content against the rules below and writes
`dist/<slug>.html`.

This file describes every part of a guide: what it's for, the fields it takes, how to
write it, and the visual cue the template gives it.

---

## 1. Top-level shape

```json
{
  "meta":     { ... },
  "entities": [ ... ],
  "hero":     { ... },
  "sections": [ ... ],
  "sources":  [ ... ]
}
```

### `meta`

| Field | Required | What it is |
|---|---|---|
| `slug` | yes | Lowercase, digits and hyphens. Becomes the output file name. |
| `title` | yes | The page name in the browser tab and gallery. 2 to 4 words, a name, not a summary. Example: `Who Cooks Your Tokens`. |
| `description` | yes | One sentence for the gallery card subtitle. |
| `eyebrow` | yes | Small label above the headline: `Field guide · <topic> · <Mon YYYY>`. |
| `researched` | yes | `YYYY-MM-DD`, the day the research was done. Shown in the footer. |
| `footer` | no | Extra footer sentence, usually a reminder about how fast prices change. |
| `published_url` | no | The artifact URL once published, so a rebuild can be republished in place. |

### `entities`

The products, services or concepts the guide teaches. Each one gets a **route color**
that the template reuses in every chip, card border, table header, diagram node and
diagram path. This is the guide's main visual cue: a reader learns "amber means Bedrock"
once and it holds for the whole page, like lines on a transit map.

```json
{ "id": "bedrock", "name": "AWS Bedrock", "hue": "amber" }
```

- `id`: lowercase, digits, hyphens. Referenced everywhere else.
- `hue`: one of `amber`, `magenta`, `teal`, `green`, `blue`, `violet`, `ink`.
- Use each hue once. **Vercel is always `ink`.** Keep it to seven entities or fewer.
- Red is reserved for risk and failure states. It is not an entity color.

### `hero`

| Field | Required | Notes |
|---|---|---|
| `headline` | yes | A question or claim that frames the whole topic. Example: `Who cooks your tokens?` |
| `lede` | yes | 2 to 3 sentences. Name the confusing thing, then promise the one idea that untangles it. |
| `chips` | yes | Entity ids, in the order they appear on the page. Rendered as a color legend. |

The template adds an "On this page" row of links under the hero automatically, using
each section's `nav` label.

### `sources`

```json
{ "title": "Fireworks pricing", "url": "https://www.fireworks.ai/pricing" }
```

Rendered as a numbered list at the end. Every fact in the guide that could go stale
(prices, fees, feature names, launch dates) should trace to one of these.

---

## 2. Inline text

Every text field accepts three bits of markup. Everything else is shown as plain text.

| Write | Get |
|---|---|
| `**bold**` | **bold** |
| `` `code` `` | `code` |
| `[label](https://example.com)` | a link that opens in a new tab |

Fields marked *paragraphs* accept a string or an array of strings (one per paragraph).

---

## 3. Sections

`sections` is an ordered array. Each item has a `type` plus that type's fields. Every
section also accepts:

| Field | Notes |
|---|---|
| `id` | Anchor for the "On this page" links. Defaults to the type plus its position. |
| `nav` | Short label (1 to 3 words) for the "On this page" row. Leave it out to skip the section there. |
| `eyebrow` | Small uppercase label above the section title, e.g. `The mental model`. |
| `title` | Section heading. |
| `intro` | *paragraphs*. Text under the heading. |

### Default order

Use this order unless the topic gives a real reason to change it. Sections marked
optional can be dropped.

| # | Type | Teaching job |
|---|---|---|
| 1 | `layers` | Give the reader the mental model and the master analogy before any detail. |
| 2 | `profile` (one per main entity) | What each thing is, why people pick it, its vocabulary, its weak spot. |
| 3 | `compare` | Line the entities up on the same rows so differences jump out. |
| 4 | `simulator` (optional) | Walk real requests or events through the customer's architecture. |
| 5 | `panels` | Interpret the architecture: why it was built this way, where it's fragile. |
| 6 | `beforeAfter` | Where Vercel fits, shown as today vs. with Vercel, plus an honest caveat. |
| 7 | `questions` | Discovery questions for the next customer call. |
| 8 | `quiz` | Five questions that check the reader learned the distinctions. |
| — | `prose` | Fallback for anything that doesn't fit the types above. Use sparingly. |

Sources and the footer are added automatically after the last section.

---

### `layers`: the mental model

Shows how the entities stack up as layers of one system, each with its analogy role.
Visual cue: horizontal bands, each with a thick left border in its entity's color.

```json
{
  "type": "layers", "nav": "Mental model",
  "eyebrow": "The mental model",
  "title": "Think of it as a restaurant district",
  "intro": "A model is a recipe. Somebody has to own the kitchen...",
  "layers": [
    { "entity": "budget", "tag": "Layer 4 · Policy", "name": "Budget profiles",
      "who": "Homegrown code in your customer's app",
      "analogy": "**The company expense policy.** Marketing gets $200 a day..." }
  ],
  "outro": "That last line is the key idea..."
}
```

Writing guidance:
- Pick **one** analogy world and map every entity to one role in it. Don't switch
  analogies later in the guide.
- Order layers top (closest to the user or business) to bottom (closest to the metal).
- Each `analogy` starts with the role in bold, then one sentence on why it fits.
- Use `outro` for the single most important idea the layers reveal.

### `profile`: one entity in depth

Visual cue: a card with a tinted header in the entity's color, a dashed "Analogy" box,
square bullets in the entity's color, a two-column glossary, and a red "Where it hurts"
box.

```json
{
  "type": "profile", "entity": "bedrock", "nav": "Bedrock",
  "eyebrow": "Kitchen #1",
  "oneLiner": "AWS's managed service for calling foundation models...",
  "analogy": "**The restaurant inside your corporate campus.** You're already badged in...",
  "why": ["**It spends money they already committed.** Bedrock usage..."],
  "terms": [["On-demand", "Pay per token, shared capacity..."]],
  "watch": "throttling on on-demand quotas, regional model availability..."
}
```

| Field | Required | Notes |
|---|---|---|
| `entity` | yes | The entity this card is about. Its name becomes the card title unless `name` is set. |
| `oneLiner` | yes | One or two sentences: what it is, in plain words. |
| `analogy` | yes | The entity's role in the master analogy, expanded with 2 to 4 concrete mappings (feature → analogy). |
| `why` | yes | 3 to 5 reasons buyers choose it. Each starts with a bold reason, then the evidence. |
| `terms` | yes | 4 to 6 `[term, definition]` pairs: the words the reader will hear on calls. |
| `watch` | yes | The weak spot or gotcha, and why it matters to the architecture. |
| `whyTitle`, `termsTitle`, `watchLabel` | no | Override the default headings ("Why people choose it", "Terms you'll hear", "Where it hurts:"). |

### `compare`: side by side

Visual cue: a table whose column headers are colored by entity. Scrolls sideways on
phones instead of squashing.

```json
{
  "type": "compare", "nav": "Compare",
  "eyebrow": "Side by side",
  "title": "Same request, three very different businesses",
  "columns": ["bedrock", "fireworks", "openrouter"],
  "rows": [ { "label": "What it is", "cells": ["...", "...", "..."] } ]
}
```

- Every row has exactly one cell per column.
- 5 to 8 rows. Always include "Buyer's main reason", "How it bills", "Classic weak spot"
  and "Typical role in a stack" or the topic's equivalents.

### `simulator`: follow it through the architecture

An interactive diagram. The reader picks a scenario, and the template highlights the
path with animated dashes in each edge's entity color, marks failures in red, and shows
numbered steps plus a one-paragraph lesson.

```json
{
  "type": "simulator", "nav": "Request flow",
  "eyebrow": "Your customer's stack",
  "title": "Follow a request through it",
  "diagram": {
    "width": 900, "height": 400,
    "nodes": [
      { "id": "app", "label": "Customer app", "sub": "request + team id",
        "x": 20, "y": 185, "w": 120, "h": 56 },
      { "id": "fw", "label": "Fireworks", "sub": "open models, tunes",
        "x": 760, "y": 185, "w": 125, "h": 56, "entity": "fireworks" }
    ],
    "edges": [
      { "id": "router-fw", "from": "router", "to": "fw", "entity": "fireworks",
        "fromShift": 5, "toShift": 5, "label": "direct", "labelAt": [585, 211] }
    ],
    "labels": [ { "x": 540, "y": 140, "text": "via OpenRouter" } ]
  },
  "scenarios": [
    { "id": "normal", "label": "Everyday request",
      "on": ["app", "app-budget", "budget"],
      "fail": [],
      "steps": ["App sends a request..."],
      "lesson": "**Note the irony:** ..." }
  ],
  "note": "This is the most likely shape based on your description..."
}
```

Diagram rules:
- Coordinates are in the diagram's own units (`width` × `height`). Lay nodes out left to
  right in the order a request travels. The diagram scrolls sideways below 720px wide.
- Node and edge ids must be unique across both lists, because scenarios name them in
  the same `on` and `fail` arrays.
- Edges connect node sides. `fromSide` and `toSide` are `right`, `left`, `top` or
  `bottom` (default right → left). `fromShift`/`toShift` nudge the attachment point so
  parallel edges don't overlap. Set `d` to an SVG path only when the automatic curve
  can't be made to work.
- A node or edge without `entity` is drawn in the neutral ink color.
- 3 to 6 scenarios. Always include the happy path, at least one failure, and one
  scenario that shows why a less obvious component exists.
- `lesson` is the takeaway, not a recap of the steps. Start it with a bold hook.
- Use `note` to say when the topology is a hypothesis that needs confirming.

### `panels`: reading the architecture

Visual cue: two or three cards side by side, each with a colored top border by tone:
`good` (green), `risk` (red) or `neutral` (grey).

```json
{
  "type": "panels", "nav": "Why & risks",
  "eyebrow": "Reading the architecture",
  "title": "Why they built it this way, and where it creaks",
  "panels": [
    { "tone": "good", "title": "The likely reasoning", "items": ["**OpenRouter for breadth.** ..."] },
    { "tone": "risk", "title": "Where it gets fragile", "items": ["**Routers stacked on routers.** ..."] }
  ]
}
```

### `beforeAfter`: where Vercel fits

Visual cue: two flow diagrams side by side. Boxes take entity colors, and one dark "hub"
box shows the Vercel product with its key features. A caveat callout with an amber left
border sits underneath.

```json
{
  "type": "beforeAfter", "nav": "Vercel fit",
  "eyebrow": "Where Vercel fits",
  "title": "AI Gateway can collapse the routing layer",
  "intro": "Vercel AI Gateway is the same kind of product as OpenRouter...",
  "before": {
    "label": "Today",
    "rows": [
      ["App", {"arrow": "→"}, {"text": "Budget code", "entity": "budget"}],
      [{"arrow": "↳"}, {"text": "OpenRouter", "entity": "openrouter"}]
    ],
    "footer": "3 bills · 2–3 retry layers · custom spend tracking"
  },
  "after": {
    "label": "With AI Gateway",
    "rows": [
      ["App (AI SDK or OpenAI client)", {"arrow": "→"}],
      {"hub": {"title": "Vercel AI Gateway", "items": ["Provider order per request..."]}},
      [{"arrow": "↳"}, {"text": "Fireworks", "entity": "fireworks"}]
    ],
    "footer": "1 routing layer · 1 dashboard"
  },
  "caveat": "**Be precise about one gap.** AI Gateway budgets don't count BYOK spend..."
}
```

- A row is either an array of items or a `{"hub": {...}}` object.
- An item is a plain string (neutral box), `{"text", "entity"}` (colored box) or
  `{"arrow": "→"}`.
- The caveat is required in spirit: always say what Vercel does **not** cover, so the
  reader never over-promises.

### `questions`: discovery questions

Visual cue: a responsive grid of cards. Each card has the question in bold and, under
it, what the answer reveals.

```json
{
  "type": "questions", "nav": "Discovery",
  "eyebrow": "For your next call",
  "title": "Discovery questions",
  "items": [ { "ask": "Who decides the route today?", "why": "Reveals stacked retries..." } ]
}
```

Write 5 to 8. Each one should map to an uncertainty in the guide (a hypothesis in the
simulator note, a "confirm" flag in a profile, the Vercel caveat).

### `quiz`: check yourself

Visual cue: one question at a time, with a score counter. Picking an answer marks it
green or red and shows the explanation.

```json
{
  "type": "quiz", "nav": "Quiz",
  "eyebrow": "Check yourself",
  "title": "Five-question quiz",
  "questions": [
    { "prompt": "A fintech has a $5M AWS commit...",
      "options": ["Fireworks serverless", "Claude on AWS Bedrock", "...", "..."],
      "answer": 1,
      "explain": "Bedrock processes data inside the AWS boundary..." }
  ]
}
```

- `answer` is the zero-based index of the correct option.
- Write scenario questions ("A customer wants X, which fits?"), not definition recall.
- Distractors should be real things from the guide, so a wrong answer still teaches.
- The `explain` says why the right answer is right **and** why the tempting wrong one isn't.

### `prose`: fallback

```json
{ "type": "prose", "eyebrow": "...", "title": "...", "intro": ["para 1", "para 2"],
  "callout": { "tone": "risk", "text": "..." } }
```

`callout.tone` is `good`, `risk` or `neutral`.

---

## 4. Visual system (owned by `template.html`)

Content files never set colors, fonts or spacing. For reference, the template provides:

| Element | Treatment |
|---|---|
| Typefaces | Bricolage Grotesque (headlines), IBM Plex Sans (body), IBM Plex Mono (eyebrows, labels, terms, code) |
| Route colors | Seven named hues, each with a strong and a soft tint, tuned separately for light and dark themes |
| Semantic colors | Green for good, red for risk and failure, amber for caveats. Never used as entity colors in the same role |
| Eyebrows | Small uppercase mono labels with wide letter spacing, above every heading |
| Analogy box | Dashed border in the entity color, labeled "Analogy" |
| Weak-spot box | Soft red fill, red bold label |
| Diagram states | Neutral grey at rest; active paths animate in the entity color; failures turn red. Animation stops for readers who prefer reduced motion |
| Themes | Light and dark, following the reader's system setting or the app's theme toggle |
| Layout | Single reading column (~70 characters) with wider breakouts for tables and diagrams; everything stacks to one column on phones |
