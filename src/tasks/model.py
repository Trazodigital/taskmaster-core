"""
@sdoc[REQ-FUNC-001]
"""

from dataclasses import dataclass


@dataclass
class Task:
    text: str
    done: bool = False


def new_task(text: str) -> Task:
    return Task(text=text)
