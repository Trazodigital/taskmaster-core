# Welcome-screen feature requirements

Feature-level requirement for a startup guide screen, derived from the approved feature sequence
diagram at `docs/design/diagrams/welcome-screen.sequence.mmd`. Shows the application's ASCII banner
and a static list of its key bindings before the task list, and stays reachable afterward on demand.

---

## REQ-FUNC-007 — show a welcome screen with the key-bindings guide

REFINES: REQ-ARCH-001

SOURCE_DIAGRAM: docs/design/diagrams/welcome-screen.sequence.mmd

STATEMENT: The application SHALL show a welcome screen carrying the ASCII banner and a static list of its key bindings before the task list on launch, dismissed by any keypress, and SHALL show it again on demand when the user presses the "?" key.

RATIONALE: A first-time user has no way to discover the app's key bindings (add/toggle/delete/cycle-filter/cycle-date-view, the add form's Tab/up/down) short of reading the source; a static guide shown first, and reachable again later, removes that barrier without building an interactive tutorial the user did not ask for.

ACCEPTANCE_CRITERIA:

- Given the application launches, When taskmaster-app mounts, Then the welcome screen is shown before the task list, carrying the ASCII banner and the key-bindings guide.
- Given the welcome screen is shown, When the user presses any key, Then the welcome screen is dismissed and the task list is shown.
- Given the task list is shown, When the user presses the "?" key, Then the welcome screen is shown again.
- Given the welcome screen is shown again via "?", When the user presses any key, Then the welcome screen is dismissed and the task list is shown.
