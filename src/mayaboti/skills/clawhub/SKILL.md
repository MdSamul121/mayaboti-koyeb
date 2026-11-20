---
name: clawhub
description: Search and install agent skills from ClawHub, the public skill registry.
homepage: https://clawhub.ai
metadata: {"mayaboti":{"emoji":"🦞"}}
---

# ClawHub

Public skill registry for AI agents. Search by natural language (vector search).

## When to use

Use this skill when the user asks any of:
- "find a skill for …"
- "search for skills"
- "install a skill"
- "what skills are available?"
- "update my skills"

## Search

```bash
npx --yes clawhub@latest search "web scraping" --limit 5
```

## Install

```bash
npx --yes clawhub@latest install <slug> --workdir ~/.mayaboti/workspace
```

Replace `<slug>` with the skill name from search results. This places the skill into `~/.mayaboti/workspace/skills/`, where mayaboti loads workspace skills from. Always include `--workdir`.

## Update

```bash
npx --yes clawhub@latest update --all --workdir ~/.mayaboti/workspace
```

## List installed

```bash
npx --yes clawhub@latest list --workdir ~/.mayaboti/workspace
```

## Notes

- Requires Node.js (`npx` comes with it).
- No API key needed for search and install.
- Login (`npx --yes clawhub@latest login`) is only required for publishing.
- `--workdir ~/.mayaboti/workspace` is critical — without it, skills install to the current directory instead of the mayaboti workspace.
- After install, remind the user to start a new session to load the skill.
