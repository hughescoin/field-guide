# field-guide skill

Research a topic and get back a visual, analogy-driven field guide page. Every guide looks
the same: the design lives in `assets/template.html`, and each guide is one JSON file.

This folder follows the open [Agent Skills](https://agentskills.io/specification) format,
so the same folder works in Claude and in other agents.

## Install

| Where | How |
|---|---|
| **Claude Desktop, claude.ai, Claude mobile** | Customize › Skills › **+** › Create skill › Upload a skill › choose `field-guide.zip`. Needs code execution ("Create and edit files") turned on. Skills belong to your account, so one upload covers every Claude app. |
| **Claude Code** | Signed in with the same Claude account (v2.1.273+), it picks up the uploaded skill automatically. Or copy this folder to `~/.claude/skills/field-guide/`. |
| **Codex** | Copy this folder to `~/.agents/skills/field-guide/` (older versions: `~/.codex/skills/`). |
| **Cursor** | Copy to `~/.cursor/skills/field-guide/`. Cursor also reads `~/.claude/skills/` and `~/.agents/skills/`. |
| **VS Code + GitHub Copilot** | Copy to `~/.copilot/skills/field-guide/`. Copilot also reads `~/.claude/skills/` and `~/.agents/skills/`. |
| **Gemini CLI, Windsurf, OpenCode and ~80 others** | `npx skills add ./field-guide -g` (Vercel's skills CLI) detects your agents and installs into each. |

One command for all coding agents at once:

```
npx skills add ./field-guide -g -y
```

## Use

Ask in plain words, for example: *"Teach me how Temporal and Inngest differ. My customer
runs background jobs on Lambda and wants durable workflows."* Most agents also let you call
it directly: `/field-guide` in Claude Code, Cursor and Copilot.

The agent researches, writes `<topic>.json` in your folder, builds `<topic>.html`, and
publishes or sends it where your app supports that.

## Change the look of every guide

Edit `assets/template.html` in your source copy, then reinstall (re-upload the zip to
Claude; rerun `npx skills add` or `npx skills update` for coding agents) and rebuild:

```
python3 scripts/build.py ~/field-guides/
```
