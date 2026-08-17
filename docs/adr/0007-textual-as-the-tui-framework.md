# 0007 — Textual as the TUI framework

## CONTEXT

`taskmaster-app`, the composition root, needs a way to render a terminal interface, dispatch key
presses to `TaskmasterState`, and redraw the task list — without introducing logic of its own, per
ADR 0001's separation of state from rendering. The stack was chosen as Python 3.14 during the
project's planning phase specifically because it added zero friction against this repository's
already-declared toolchain, but which TUI library to use inside that choice was left open until
code was about to be written.

## DECISION

Build `taskmaster-app` on Textual.

## RATIONALE

Textual is an event-driven TUI framework with a widget model (`Input`, `ListView`) that maps
directly onto this feature's needs — a text field and a list — without hand-rolling terminal
control sequences. Its `App` class is a natural home for the composition root: one class,
instantiated once, that owns the Textual event loop and is the only place that constructs the
concrete `JsonFileRepository` and hands it to `TaskmasterState`. Because ADR 0001 already keeps all
business logic in `TaskmasterState`, the Textual layer stays thin — key bindings and widget
plumbing only — so the dependency is scoped to rendering and does not spread into `tasks` or
`storage`.

## ALTERNATIVES

- **`curses` (stdlib)** — rejected: no widget model, so `Input`-equivalent text entry and list
  rendering would be hand-built and hand-tested, which is exactly the kind of code this project's
  strict-TDD rule makes expensive to carry.
- **`prompt_toolkit`** — rejected: capable, but oriented around building a single prompt/REPL rather
  than a multi-widget application; would need more scaffolding to get the same list-plus-input shape
  Textual provides directly.
- **A hand-rolled ANSI renderer** — rejected outright: reimplements what a maintained library already
  does, for a personal tool where that effort buys nothing.

## CONSEQUENCES

### POSITIVE

- `Input` and `ListView` cover this feature's UI needs with no custom widget code.
- The composition root maps directly onto Textual's `App` class — one class, one instantiation site.

### NEGATIVE

- A new runtime dependency, with its own release cadence to track.
- Testing key-driven behavior through Textual's own async test harness would need an additional dev
  dependency (`pytest-asyncio` or `anyio`); this feature avoids that by keeping `taskmaster-app`
  free of independent logic — everything it does is already covered by `TaskmasterState`'s tests,
  and the Textual layer itself is checked only structurally (see `docs/design/add-task.md`).

## STATUS

Accepted

## RELATED_REQS

- REQ-FUNC-001
- REQ-ARCH-001
- REQ-ARCH-013
