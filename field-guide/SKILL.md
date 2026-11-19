---
name: field-guide
description: Research a technology, vendor or customer architecture and teach it as a visual field guide page with one master analogy, color-coded diagrams, an interactive scenario walkthrough, discovery questions, a Vercel angle and a quiz. Use when a Vercel solutions architect asks to learn, understand or be taught a topic, product or customer stack.
---

# Field Guide

Turns a topic into a visual, analogy-driven guide that a solutions architect at Vercel can
read once and then use on customer calls. Every guide looks the same because the design
lives in one file and each topic is only a content file.

## Files

| File | What it is |
|---|---|
| `template.html` | **The only design file.** Colors, type, spacing and every section layout. Change it here and every guide changes on rebuild. |
| `build.py` | Validates a content file and writes `dist/<slug>.html`. Python 3 standard library only. |
| `reference/guide-format.md` | Every section type: purpose, fields, writing guidance and visual cue. Read it before writing content. |
| `guides/<slug>.json` | One content file per topic. `guides/ai-inference-routing.json` is the reference example. |

## Workflow

### 1. Scope
Pin down, from the request:
- **Topic and entities.** The 2 to 5 products, services or concepts to teach. Add the
  customer's own homegrown pieces as entities when they matter (e.g. "Homegrown budgets").
- **Customer context.** The architecture or situation that prompted the question. If
  there isn't one, the simulator becomes a generic reference architecture.
- **Vercel angle.** Which Vercel product touches this (AI Gateway, Functions, Fluid
  compute, AI SDK, Sandbox, Marketplace integrations...), or that none does.

If the customer context is missing and would change the guide, ask one question.
Otherwise start.

### 2. Research
- Search for each entity separately. Prefer vendor docs, pricing pages and changelogs.
- Search vercel.com docs and changelog for the Vercel angle, even if you think you know it.
- Anything that changes (prices, fees, limits, feature names, model lists) needs a
  source and an "as of" month in the text.
- When only one source supports a claim, or sources conflict, keep the claim but flag it
  in the text ("A pricing tracker reports... Confirm it with them.") and turn it into a
  discovery question.
- Record every source you rely on for `sources`.
- Paraphrase. No quote longer than 15 words, at most one quote per source.

### 3. Choose the master analogy
- One world (a restaurant district, an airport, a power grid, a shipping port...).
- Every entity gets exactly one role in it, and each layer of the system maps to a
  layer of the analogy.
- Test it: you should be able to explain each entity's main trade-off and its weak
  spot inside the analogy. If you can't, pick another world.
- Reuse it everywhere: layers, every profile's analogy box, scenario lessons.

### 4. Assign colors
One hue per entity from `amber`, `magenta`, `teal`, `green`, `blue`, `violet`, `ink`.
Vercel is always `ink`. Red is reserved for risk. Use a spare hue (via `hue`) for layers
or diagram nodes that aren't entities.

### 5. Write the content file
Create `guides/<slug>.json`. Start by copying the reference example's structure. Follow
the default section order in `reference/guide-format.md`:

1. `layers`: mental model
2. `profile`: one per main entity
3. `compare`: side by side
4. `simulator`: scenarios through the architecture (optional when there's no flow)
5. `panels`: why it was built this way / where it's fragile
6. `beforeAfter`: where Vercel fits, with an honest caveat
7. `questions`: discovery questions
8. `quiz`: five scenario questions

### 6. Build and validate
```
python3 build.py guides/<slug>.json
```
Fix every error. Read every warning and fix it unless you have a reason not to.

### 7. Check the work
- Re-read each fact against its source, especially numbers and dates.
- Check each quiz answer is actually correct and its explanation addresses the tempting
  wrong option.
- If you can render pages, look once at desktop and phone widths in light and dark.
  The simulator must show a sensible path for every scenario.

### 8. Deliver
- If an artifact or page-publishing tool is available, publish `dist/<slug>.html`
  as-is, then save the URL to `meta.published_url`. To update a guide later, republish
  to that URL.
- Otherwise, hand over `dist/<slug>.html` as a file.
- Reply with one line on what the guide covers, the one or two claims the reader should
  verify before using them with a customer, and a Sources list.

## Writing rules
- Write for a technical reader who is new to this topic. Define every acronym once.
- Short, plain sentences in active voice. No em-dash asides, no "not X, but Y" framing.
- Bold the first few words of a list item to make it scannable, then explain.
- Every section should teach a distinction, not repeat the one before it.
- Say what's uncertain. Hypotheses about the customer's architecture go in the simulator
  `note`, and each one should have a matching discovery question.
- The Vercel section must say what Vercel does **not** cover. The reader should never
  over-promise on a call.

## Changing the design
1. Edit `template.html` only. Content files never contain colors, fonts or layout.
2. Bump `TEMPLATE_VERSION` in its script (it shows in every guide's footer).
3. Run `python3 build.py --all` to rebuild every guide.
4. Republish each guide that has a `published_url`.

To add a new section type: add a renderer to the `R` object in `template.html`, add its
required fields to `SECTION_FIELDS` in `build.py`, and document it in
`reference/guide-format.md`.

## Without Python
If the agent can't run Python, build by hand: copy `template.html`, replace `{{TITLE}}`
and `{{DESCRIPTION}}` with the meta values, and replace `{{DATA}}` with the content JSON
(change every `<` inside it to `<`). Then check the content against
`reference/guide-format.md` yourself, since nothing will validate it.
