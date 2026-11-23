---
name: field-guide
description: Research a technology, vendor, product or customer architecture and teach it as a visual, analogy-driven field guide, a single HTML page with color-coded diagrams, an interactive scenario walkthrough, a side-by-side comparison, discovery questions, where Vercel fits, and a quiz. Use when someone asks to learn, understand, explain or be taught a topic, tool, vendor or customer stack, or asks for a field guide, explainer or learning report, especially for solutions architecture and customer discovery calls.
metadata:
  version: "1.1"
  author: field-guide kit
---

# Field Guide

Turns a topic into a visual, analogy-driven guide that a Vercel solutions architect reads
once and then uses on customer calls. Every guide looks the same because the design lives
in one template file and each topic is only a content file.

## Files in this skill

All paths below are relative to the folder that contains this SKILL.md. In Claude Code and
Cowork that folder is `${CLAUDE_SKILL_DIR}`. In other agents, use the folder you loaded this
file from.

| File | Use it to |
|---|---|
| `references/guide-format.md` | Learn every section type, its fields and how to write it. **Read before writing content.** |
| `assets/example-ai-inference-routing.json` | See a complete, valid guide. Copy its structure, not its content. |
| `assets/template.html` | The design. Never edit it while making a guide. |
| `scripts/build.py` | Validate a content file and build the page. Python 3.8+, standard library only. |

## Workflow

### 1. Scope
From the request, settle:
- **Topic and entities.** The 2 to 5 products, services or concepts to teach. Add the
  customer's homegrown pieces as entities when they matter (e.g. "Homegrown budgets").
- **Customer context.** The architecture or situation behind the question. Without one,
  the simulator shows a generic reference architecture.
- **Vercel angle.** Which Vercel product touches this (AI Gateway, Functions, Fluid
  compute, AI SDK, Sandbox, Marketplace integrations...), or that none does.

If missing customer context would change the guide, ask one question. Otherwise start.

### 2. Research
- Search for each entity separately. Prefer vendor docs, pricing pages and changelogs.
- Search vercel.com docs and changelog for the Vercel angle, even if you think you know it.
- Anything that changes (prices, fees, limits, feature names, model lists) needs a source
  and an "as of" month in the text.
- When only one source supports a claim, or sources conflict, keep it but flag it in the
  text ("A pricing tracker reports... Confirm it with them.") and add a discovery question.
- Record every source you rely on for `sources`. Paraphrase; quote at most 15 words.
- **No web search available?** Say so to the user before you start, write from what you
  know, set every time-sensitive claim as "unverified as of <your knowledge date>", and
  leave `sources` with only links you are sure exist.

### 3. Choose the master analogy
- One world (a restaurant district, an airport, a power grid, a shipping port...).
- Every entity gets exactly one role in it; each layer of the system maps to a layer of it.
- Test it: you should be able to explain each entity's main trade-off and weak spot inside
  the analogy. If you can't, pick another world.
- Reuse it everywhere: layers, every profile's analogy box, scenario lessons.

### 4. Assign colors
One hue per entity from `amber`, `magenta`, `teal`, `green`, `blue`, `violet`, `ink`.
Vercel is always `ink`. Red is reserved for risk. Give layers or diagram nodes that aren't
entities a spare hue with `hue`.

### 5. Write the content file
Save it as `<slug>.json` in the user's folder, never inside the skill folder (it may be
read-only and is replaced on update). Use the folder the user named; otherwise a
`field-guides/` folder in the working directory, or your environment's outputs folder if
it has one. Follow the default section order in `references/guide-format.md`:

1. `layers`: mental model
2. `profile`: one per main entity
3. `compare`: side by side
4. `simulator`: scenarios through the architecture (skip when there's no flow)
5. `panels`: why it was built this way / where it's fragile
6. `beforeAfter`: where Vercel fits, with an honest caveat
7. `questions`: discovery questions
8. `quiz`: five scenario questions

### 6. Build and validate
```
python3 scripts/build.py <path-to>/<slug>.json
```
This writes `<slug>.html` next to the JSON: a complete page that opens in any browser.
Fix every error. Fix every warning unless you have a reason not to. Use `python3` or
`python`, whichever exists.

### 7. Check the work
- Re-read each fact against its source, especially numbers and dates.
- Check each quiz answer is correct and its explanation covers the tempting wrong option.
- If you can render pages (a browser tool, Playwright, a preview), look once at desktop
  and phone widths. Every simulator scenario should light a sensible path.

### 8. Deliver
Pick the first that fits your environment:
- **A tool that publishes an HTML file as a page or artifact.** Publish the built file
  itself. If the tool says it adds its own `<!doctype>`/`<html>`/`<body>` wrapper, build
  again with `--fragment` and publish `<slug>.fragment.html` instead. Save the resulting
  URL to `meta.published_url`; republish to that URL when updating.
- **A tool that sends or attaches files to the user.** Send `<slug>.html`.
- **Neither (a local coding agent).** Tell the user the file's full path and that it opens
  in any browser. Offer to open it if you can run a command.

Never retype or paste the built HTML into a reply or an artifact by hand. It is large and
copying it by hand corrupts it.

Reply with one line on what the guide covers, the one or two claims to verify before
using them with a customer, and a Sources list.

## Writing rules
- Write for a technical reader who is new to this topic. Define every acronym once.
- Short, plain sentences in active voice. No em-dash asides, no "not X, but Y" framing.
- Bold the first few words of a list item to make it scannable, then explain.
- Every section should teach a distinction, not repeat the one before it.
- Say what's uncertain. Hypotheses about the customer go in the simulator `note`, each with
  a matching discovery question.
- The Vercel section must say what Vercel does **not** cover, so the reader never
  over-promises on a call.

## Updating an existing guide
Edit its JSON, rebuild, and republish to `meta.published_url` if it has one.

## Changing the design for every guide
Only when the user asks to change the look:
1. Edit `assets/template.html` (in the user's source copy of the skill, not an installed
   read-only copy). Bump `TEMPLATE_VERSION` in its script.
2. Rebuild a whole folder of guides: `python3 scripts/build.py <guides-folder>/`.
3. Republish each guide that has a `published_url`.

To add a section type: add a renderer to the `R` object in the template, its required
fields to `SECTION_FIELDS` in `scripts/build.py`, and its docs to `references/guide-format.md`.

## No Python available
Build by hand with file tools: read `assets/template.html`, replace `{{TITLE}}` and
`{{DESCRIPTION}}` with the meta values, replace `{{DATA}}` with the content JSON (change
every `<` inside the JSON to `\u003c`), and write the result as `<slug>.html` starting with
`<!doctype html>`. Check the content against `references/guide-format.md` yourself, since
nothing will validate it. If you can't write files at all, give the user the JSON and the
build command to run later.
