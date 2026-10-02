# How Copilot's File Layout Maps to Claude's

## The configuration ecosystems mirror each other across multiple layers

| Context Scope | Claude File Standard | GitHub Copilot File Standard |
| ----------- | ----------- | ----------- |  
| Global / User-Level | ~/.claude/CLAUDE.md | ~/.copilot/copilot-instructions.md |
| Project / Repo Root | CLAUDE.md | .github/copilot-instructions.md |
| Folder / Sub-directory | .claude/rules/ | .github/instructions/*.instructions.md |
| Cross-Assistant Standard | AGENTS.md | AGENTS.md (Supported natively as a shared fallback) |

## Typical Repo Structure

```python
my-project/
├── .git/                      <-- (Internal Git data—leave this alone)
├── .github/                   <-- (Create this folder)
│   └── copilot-instructions.md <-- (Your Copilot base prompt file)
├── AGENTS.md                  <-- (Live standard fallback file goes here)
├── CLAUDE.md                  <-- (Your Claude base prompt file, if using Claude)
├── src/
├── package.json
└── README.md
```

## Pro-Tip for Multi-AI Workspaces

If your team uses both Claude and Copilot, the newest AI agent standards allow you to use a shared file named AGENTS.md placed directly at your repository root. Both modern versions of Copilot and the VS Code Claude extension will read AGENTS.md as a fallback so you don't have to duplicate your prompt instructions across different file paths.
