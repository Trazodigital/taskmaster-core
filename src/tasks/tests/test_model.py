"""
@sdoc[REQ-FUNC-001]
@sdoc[REQ-FUNC-002]
@sdoc[REQ-FUNC-004]
"""

from tasks.model import by_space, distinct_spaces, new_task, toggle_done


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


def test_new_task_parses_a_trailing_space_tag():
    """@sdoc[REQ-FUNC-004]"""
    task = new_task("buy bread @work")

    assert task.text == "buy bread"
    assert task.space == "work"


def test_new_task_with_no_space_tag_has_an_empty_space():
    """@sdoc[REQ-FUNC-004]"""
    task = new_task("buy bread")

    assert task.space == ""


def test_distinct_spaces_returns_each_space_once_excluding_empty():
    """@sdoc[REQ-FUNC-004]"""
    tasks = [
        new_task("buy bread @home"),
        new_task("walk the dog @home"),
        new_task("ship the release @work"),
        new_task("water the plants"),
    ]

    assert distinct_spaces(tasks) == ["home", "work"]


def test_by_space_returns_only_matching_tasks():
    """@sdoc[REQ-FUNC-004]"""
    tasks = [new_task("buy bread @home"), new_task("ship the release @work")]

    assert [t.text for t in by_space(tasks, "home")] == ["buy bread"]


def test_by_space_is_deterministic():
    """@sdoc[REQ-FUNC-004]"""
    tasks = [new_task("buy bread @home"), new_task("ship the release @work")]

    assert by_space(tasks, "home") == by_space(tasks, "home")
