# Domain glossary

Single canonical vocabulary for this project. Every domain term that appears
in any file under `docs/requirements/` or `docs/design/` is defined here
exactly once. No synonyms in requirements or designs — always the term
defined here.

This file is authored and modified only through the `domain-glossary`
skill (`skills/domain-glossary/SKILL.md`). Its structural invariants are
enforced by `scripts/check-glossary.sh`.

### Authoring rules

- **One entry per term.** No duplicates (case-insensitive).
- **One-sentence definition.** Precise, unambiguous, present tense.
- **Examples are optional** but strongly encouraged when the concept is subtle.
- **Aliases are optional.** Use them only to record deprecated names during a
  rename; requirements and designs MUST use the canonical `TERM`.
- **No orphan entries.** Every term listed here MUST appear at least once in
  `docs/requirements/` or `docs/design/`. `scripts/check-glossary.sh` rejects
  orphans.
- **No introduction outside the skill.** New terms enter this file only via
  the `domain-glossary` skill's `introduce` operation.

### Entry format

Each entry uses this exact shape:

```markdown
## <TERM>

**Definition:** <one sentence>
**Examples:** <optional, one or more>
**Aliases:** <optional, comma-separated>
```

Rules the parser enforces:

- `## <TERM>` is a top-level heading (exactly two `#`).
- `**Definition:**` MUST appear before the next `## ` heading.
- Content inside fenced code blocks (```` ``` ````) is ignored by the parser,
  so the format example above is safe.

### Terms

<!--
  Entries below this line are appended by the `domain-glossary` skill during
  Phase 1 (`sdd-spec`). This section is empty in the framework template.
-->

## task

**Definition:** A single unit of work the user tracks, carrying a text description, a completion state, a space, and an optional due date.
**Examples:** "buy bread"; "send the invoice", due 2026-08-20, space "work".

## space

**Definition:** A free-text label on a task that groups it by context, and which exists only while at least one task names it.
**Examples:** work; school; personal.

## overdue

**Definition:** The state of a task that is not complete and whose due date is earlier than the current date.

## filter

**Definition:** The combination of space and date view currently selected by the user, determining which tasks are presented.
**Examples:** space "work" with the today view; no space with the overdue view.

## due this week

**Definition:** The state of a task that is not complete and whose due date falls within the next seven days counting from the current date, inclusive of today.
**Examples:** on 2026-08-17, a task due 2026-08-17 through 2026-08-23 is due this week; one due 2026-08-24 is not.

## store

**Definition:** The single local file in which task records are persisted between runs of the application.

## file fingerprint

**Definition:** A value derived from the store at read time, compared before a later write to detect whether the store changed outside the application.
