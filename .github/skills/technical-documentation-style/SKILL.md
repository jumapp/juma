---
name: technical-documentation-style
description: "Write and revise technical documentation in a terse, requirement-driven style for software specifications, architecture docs, API documentation, user journeys, implementation plans, and UX/UI flows. Use when creating or elaborating project documentation for a technical team."
argument-hint: "Describe the document or section to write, revise, or elaborate"
user-invocable: true
disable-model-invocation: false
---

# Technical Documentation Style

## Purpose

Produce accurate, decision-useful technical documentation for a senior technical architect and software engineer. The writing must be concise, structured, implementation-aware, and usable by a small technical team.

## Workflow

1. Identify the document's purpose, audience, scope, and status.
   - Mark statements as current, proposed, required, or unresolved when the distinction matters.
   - Inspect the repository and existing docs before asserting project-specific facts.
2. Organize the document from top to bottom.
   - Start with purpose, scope, and key outcomes.
   - Follow with requirements, user behavior, architecture, data/API contracts, implementation details, and validation.
   - Keep unrelated concerns in separate sections.
3. State behavior as testable requirements.
   - Use phrasing such as "The app must...", "The user must be able to...", and "Only ... can...".
   - Include states, edge cases, failure handling, permissions, offline behavior, and platform differences when relevant.
4. Cover architecture and engineering consequences.
   - Name concrete technologies, modules, interfaces, dependencies, and ownership boundaries.
   - Describe data flow, persistence, synchronization, error handling, security, observability, performance, and deployment impact when relevant.
   - Prefer existing repository patterns and APIs over invented abstractions.
5. Cover UX/UI as behavior, not decoration.
   - Document hierarchy, navigation, affordances, loading/empty/error/success states, validation, accessibility, responsive behavior, and iOS/Android/Web differences.
   - Specify what the user sees, can do, and expects at each important transition.
   - Include keyboard, touch, screen-reader, contrast, focus, and reduced-motion considerations when applicable.
6. Record uncertainty explicitly.
   - Add an `Open Questions` or `Unresolved Decisions` section for missing information.
   - Do not silently invent requirements, metrics, APIs, or implementation details.
   - Use short scratchpad directives as blockquotes only when a note does not belong in a requirement list.
7. Validate the result.
   - Check terminology, capitalization, links, code identifiers, and internal consistency.
   - Verify requirements are specific enough to implement and test.
   - Remove repetition, marketing language, unsupported claims, and empty explanation.

## Structure and Voice

- Default to clean Markdown with `##` and `###` headings, short sections, bullets, numbered procedures, tables only when comparison benefits from them, and `---` between major parts.
- Prefer nested bullets for discrete requirements. Use paragraphs only for concise context or rationale.
- Use a terse, functional, technically literate voice. Every bullet must add information.
- Use first-person plural for team decisions when useful: "We need to...".
- Use inline code for identifiers, commands, files, libraries, endpoints, configuration keys, and technologies.
- Keep terminology consistent throughout the document. Define an unfamiliar term once, then reuse it consistently.
- Avoid marketing language, corporate PRD phrasing, "As a user, I want..." templates, filler, and essay-like exposition.
- Do not use grammatical errors, spelling errors, vague passive requirements, or unexplained acronyms.

## Elaboration Mode

When asked to elaborate, expand only the named section. Preserve its existing voice and structure. Add concrete sub-requirements, examples, edge cases, technical constraints, UX states, or validation criteria. Do not rewrite unrelated sections or add padding.

## Output Checklist

Before returning documentation, confirm:

- Purpose, scope, audience, and document status are clear.
- Requirements are specific, testable, and ordered by importance.
- Current facts are separated from proposals and open questions.
- Architecture, API/data, security, offline, and deployment concerns are covered when applicable.
- UX/UI behavior includes states, accessibility, responsive layout, and platform differences when applicable.
- Technical names and repository references are accurate.
- Markdown is clean, concise, and free of repetition or unsupported claims.
