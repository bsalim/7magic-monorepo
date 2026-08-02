# 7magic Monorepo

This repository is the working home for the 7magic article and marketplace platform.

## Project Shape

- `apps/web` — SvelteKit public wedding website.
- `apps/cms` — SvelteKit CMS/backend management app.
- `apps/api` — FastAPI API for public website and CMS.
- `.agents/skills` — local Codex skillset copied from the Aire setup.
- `.claude/skills` — local Claude/GitNexus skill references copied from the Aire setup.

## Repository Conventions

- Keep product and business-specific code inside the relevant app.
- Do not copy source code from Aire Wellness into this project.
- Prefer small, focused changes and follow the existing app structure.
- Use `rg` for search.
- Use `apply_patch` for manual file edits.

## GitNexus

This repository is indexed by GitNexus. Refresh the index after meaningful code passes:

```bash
npx gitnexus analyze
```

Generated GitNexus instructions for `7magic-monorepo` are below.

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **7magic-monorepo** (1927 symbols, 3077 relationships, 69 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/7magic-monorepo/context` | Codebase overview, check index freshness |
| `gitnexus://repo/7magic-monorepo/clusters` | All functional areas |
| `gitnexus://repo/7magic-monorepo/processes` | All execution flows |
| `gitnexus://repo/7magic-monorepo/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
