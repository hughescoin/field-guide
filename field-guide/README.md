# Field Guide kit

Make visual, analogy-driven learning guides that all look the same.

```
field-guide/
├── SKILL.md                    workflow an agent follows (research → content → build → publish)
├── template.html               the ONE design file: colors, type, layouts for every section
├── build.py                    validates content and builds dist/<slug>.html
├── reference/guide-format.md   every section type, its fields and how to write it
├── guides/
│   └── ai-inference-routing.json   reference example (Bedrock, Fireworks, OpenRouter)
└── dist/
    └── ai-inference-routing.html   built page
```

**New guide:** write `guides/<topic>.json`, then `python3 build.py guides/<topic>.json`.

**Change the look of every guide:** edit `template.html`, then `python3 build.py --all`.

**Check content without building:** `python3 build.py --check guides/<topic>.json`.
