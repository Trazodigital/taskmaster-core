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

## Task

**Definition:** A unit of work tracked by TaskMaster Core, optionally carrying a Due Date and optionally assigned to a Space.
**Examples:** "Write the architecture doc", "Renew the domain"

## Space

**Definition:** A named container that groups related Tasks so they can be organized and retrieved together.
**Examples:** "Work", "Home", "Q3 launch"

## Due Date

**Definition:** The instant at which a Task becomes due, used by `tasks` to decide whether the Task is an Overdue Task.

## Overdue Task

**Definition:** A Task whose Due Date lies in the past at the moment a due-date check runs.

## Reminder

**Definition:** A single message delivered to the User announcing one Overdue Task.

## Command

**Definition:** A single instruction issued by the User through `cli`, such as creating a Task, listing Tasks, or assigning a Task to a Space.
**Examples:** create task, list tasks, assign task to space

## Task List

**Definition:** The ordered collection of Tasks returned by a task-listing Command, possibly empty.
