"""
@sdoc[REQ-FUNC-001]
"""

from tasks.model import new_task


def test_new_task_from_text_is_not_done():
    """@sdoc[REQ-FUNC-001]"""
    task = new_task("buy bread")

    assert task.text == "buy bread"
    assert task.done is False
