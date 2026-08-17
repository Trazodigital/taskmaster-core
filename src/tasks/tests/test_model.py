"""
@sdoc[REQ-FUNC-001]
@sdoc[REQ-FUNC-002]
"""

from tasks.model import new_task, toggle_done


def test_new_task_from_text_is_not_done():
    """@sdoc[REQ-FUNC-001]"""
    task = new_task("buy bread")

    assert task.text == "buy bread"
    assert task.done is False


def test_toggle_done_flips_a_not_done_task_to_done():
    """@sdoc[REQ-FUNC-002]"""
    task = new_task("buy bread")

    flipped = toggle_done(task)

    assert flipped.done is True
    assert flipped.text == "buy bread"


def test_toggle_done_flips_a_done_task_back_to_not_done():
    """@sdoc[REQ-FUNC-002]"""
    task = toggle_done(new_task("buy bread"))

    flipped_back = toggle_done(task)

    assert flipped_back.done is False
