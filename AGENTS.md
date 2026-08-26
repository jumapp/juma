# Project Rules

## Project Overview

Before starting work, read `/README.md` for project overview, structure, setup, API, and conventions. Then follow the rules below.

## Use available skills 

Use **skill-driven execution model** powered by the `skill` tool and this repository's `/skills` directory.

### Core Rules

- If a task matches a skill, you MUST invoke it
- Skills are located in `skills/<skill-name>/SKILL.md`
- Never implement directly if a skill applies
- Always follow the skill instructions exactly (do not partially apply them)

### Intent → Skill Mapping

The agent should automatically map user intent to skills:

- Feature / new functionality → `spec-driven-development`, then `incremental-implementation`, `test-driven-development`
- Planning / breakdown → `planning-and-task-breakdown`
- Bug / failure / unexpected behavior → `debugging-and-error-recovery`
- Code review → `code-review-and-quality`
- Refactoring / simplification → `code-simplification`
- API or interface design → `api-and-interface-design`
- UI work → `frontend-ui-engineering`

### Lifecycle Mapping (Implicit Commands)

OpenCode does not support slash commands like `/spec` or `/plan`.

Instead, the agent must internally follow this lifecycle:

- DEFINE → `spec-driven-development`
- PLAN → `planning-and-task-breakdown`
- BUILD → `incremental-implementation` + `test-driven-development`
- VERIFY → `debugging-and-error-recovery`
- REVIEW → `code-review-and-quality`
- SHIP → `shipping-and-launch`

### Execution Model

For every request:

1. Determine if any skill applies (even 1% chance)
2. Invoke the appropriate skill using the `skill` tool
3. Follow the skill workflow strictly
4. Only proceed to implementation after required steps (spec, plan, etc.) are complete

### Anti-Rationalization

The following thoughts are incorrect and must be ignored:

- "This is too small for a skill"
- "I can just quickly implement this"
- "I'll gather context first"

Correct behavior:

- Always check for and use skills first

This ensures OpenCode behaves similarly to Claude Code with full workflow enforcement.


## Cross-Platform (iOS / Android / Web)
- All code must work on iOS, Android, and Web.
- Use `Platform.OS` guards for platform-specific behavior.
- Never import web-only APIs (e.g. `window`, `document`, service workers) without a `Platform.OS === 'web'` check.

## Offline Support
- The app must work offline on all platforms.
- Web: service worker + CacheStorage for app shell and assets.
- Native: AsyncStorage / expo-file-system for data persistence.
- Always provide offline fallbacks for network-dependent features.

## PWA
- Use `public/manifest.json` for the PWA manifest and `app/+html.tsx` to link it (static rendering).
- Keep `public/manifest.json` and `public/service-worker.js` in sync with `app.json`.
- Service worker must use Cache-First for static assets and Network-First for API data.
