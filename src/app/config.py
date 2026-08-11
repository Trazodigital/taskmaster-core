"""The single site that reads runtime configuration from the environment.

Every value is validated here, at startup, so a misconfigured run fails before
it touches the store rather than halfway through a write.

@sdoc[REQ-FUNC-007]
@no-runtime-events[REQ-FUNC-007]
"""

from pathlib import Path

#: Declared in ``.env.example``. The default keeps a fresh checkout runnable.
STORE_PATH_VARIABLE = "TASKMASTER_STORE_PATH"
DEFAULT_STORE_PATH = "taskmaster.json"


class ConfigError(Exception):
    """A configuration value was supplied but is unusable."""


def store_path(env):
    """Resolve the JSON store path, rejecting a supplied-but-blank value.

    An unset variable falls back to the default; a variable set to whitespace
    is an operator mistake and is never silently defaulted over.

    @sdoc[REQ-FUNC-007]
    """
    configured = env.get(STORE_PATH_VARIABLE)

    if configured is None:
        return Path(DEFAULT_STORE_PATH)

    if not configured.strip():
        raise ConfigError(f"{STORE_PATH_VARIABLE} is set but empty")

    return Path(configured.strip())
