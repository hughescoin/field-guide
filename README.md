# teach-me

Get a study guide for one concept or a list of them.

This repo holds the **field-guide** skill. You give an agent a topic. It researches the
topic and builds a single HTML page that teaches it, with an analogy, color-coded diagrams,
a scenario walkthrough, a side-by-side comparison, discovery questions and a quiz.

The skill uses the open [Agent Skills](https://agentskills.io/specification) format: a
folder with a `SKILL.md` file of instructions plus the files those instructions use. Any
agent that can read files can follow it.

```
field-guide/
├── SKILL.md                     # instructions the agent follows
├── references/guide-format.md   # the content format, section by section
├── assets/template.html         # the page design shared by every guide
├── assets/example-…json         # a complete example guide
└── scripts/build.py             # validates a guide and builds the HTML (Python 3.8+)
```

## Quick install

One command installs the skill into every coding agent on your machine (Claude Code,
Codex, Cursor, Copilot, Gemini CLI, Windsurf and others). You don't need to clone this
repo first:

```
npx skills add https://github.com/hughescoin/teach-me/tree/main/field-guide -g -y
```

For the Claude apps, or to install by hand, see the sections below.

## Get the skill

```
git clone https://github.com/hughescoin/teach-me.git
cd teach-me
```

Install it once for each place you work.

## Claude Desktop, claude.ai and Claude mobile

Zip the folder, then upload it.

```
zip -r field-guide.zip field-guide
```

Go to **Customize › Skills › + › Create skill › Upload a skill** and choose
`field-guide.zip`. Code execution ("Create and edit files") must be on. Skills belong to
your account, so one upload covers every Claude app.

## Claude Code

If you uploaded the skill to your Claude account (above), sign in to Claude Code with the
same account and it loads the skill automatically.

Otherwise, copy the folder into your skills directory and start a new session:

```
mkdir -p ~/.claude/skills
cp -R field-guide ~/.claude/skills/
```

To share it with one project only, copy it to `.claude/skills/field-guide/` inside that
project instead.

## Codex, Cursor, VS Code with Copilot, Gemini CLI, Windsurf and others

Vercel's [skills CLI](https://github.com/vercel-labs/skills) finds the agents on your
machine and installs the skill into each one. You don't need to publish the skill anywhere
first.

From your clone:

```
npx skills add ./field-guide -g -y
```

Or straight from GitHub, without cloning:

```
npx skills add https://github.com/hughescoin/teach-me/tree/main/field-guide -g -y
```

`-g` installs for your user account instead of only the current project. `-y` skips the
confirmation prompts.

**Without npx:** Codex, Cursor and Copilot all read the shared `~/.agents/skills/` folder,
so you can copy it there yourself and restart the agent:

```
mkdir -p ~/.agents/skills
cp -R field-guide ~/.agents/skills/
```

## Grok and other agents

Agents that don't load skill folders can still follow the skill, because `SKILL.md` is
plain instructions.

**If the agent can read and write files** (a coding agent, or a chat agent with code
execution), point it at the skill:

> Read `field-guide/SKILL.md` and follow it to make a field guide about *\<topic\>*.

It reads the format guide, writes `<topic>.json` and runs `scripts/build.py` to make
`<topic>.html`.

**If the agent can only chat** (for example Grok in a browser):

1. Start the chat with the contents of `field-guide/SKILL.md` and
   `field-guide/references/guide-format.md`. Paste them, attach them, or save them as
   project or custom instructions if your agent supports that.
2. Attach `field-guide/assets/example-ai-inference-routing.json` as a model to copy.
3. Ask for a guide on your topic. The agent replies with the guide's JSON.
4. Save that reply as `<topic>.json` and build the page on your own machine:

   ```
   python3 field-guide/scripts/build.py <topic>.json
   ```

   Open `<topic>.html` in any browser. If the build reports errors, paste them back to the
   agent and ask it to fix the JSON.

## Use it

Ask in plain words, for example *"Teach me how Temporal and Inngest differ. My customer
runs background jobs on Lambda."* In Claude Code, Cursor and Copilot you can also type
`/field-guide`.

## Build or rebuild a guide yourself

```
python3 field-guide/scripts/build.py my-topic.json         # validate and build one guide
python3 field-guide/scripts/build.py ~/field-guides/       # rebuild a whole folder
python3 field-guide/scripts/build.py --check my-topic.json # validate only
```

The script uses only the Python standard library. More detail on installing, using and
restyling the skill is in [`field-guide/README.md`](field-guide/README.md).
