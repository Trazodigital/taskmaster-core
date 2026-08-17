"""
@sdoc[REQ-FUNC-001]
@sdoc[REQ-FUNC-002]
@sdoc[REQ-FUNC-004]
@sdoc[REQ-FUNC-005]
@sdoc[REQ-FUNC-006]
"""

from datetime import date

from tasks.model import (
    build_task,
    by_space,
    distinct_spaces,
    due_this_week,
    due_today,
    is_overdue,
    new_task,
    overdue,
    toggle_done,
)


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


def test_new_task_parses_a_trailing_due_date():
    """@sdoc[REQ-FUNC-005]"""
    task = new_task("send the invoice !2026-08-20")

    assert task.text == "send the invoice"
    assert task.due_date == date(2026, 8, 20)


def test_new_task_with_no_due_date_tag_has_no_due_date():
    """@sdoc[REQ-FUNC-005]"""
    task = new_task("buy bread")

    assert task.due_date is None


def test_new_task_with_an_unparseable_date_tag_keeps_it_as_literal_text():
    """@sdoc[REQ-FUNC-005]"""
    # a typo in the date must never crash task creation
    task = new_task("buy bread !not-a-date")

    assert task.text == "buy bread !not-a-date"
    assert task.due_date is None


def test_new_task_parses_both_a_space_and_a_due_date_tag():
    """@sdoc[REQ-FUNC-005]"""
    task = new_task("send the invoice !2026-08-20 @work")

    assert task.text == "send the invoice"
    assert task.due_date == date(2026, 8, 20)
    assert task.space == "work"


def test_due_today_excludes_done_tasks_and_other_dates():
    """@sdoc[REQ-FUNC-005]"""
    today = date(2026, 8, 17)
    due_today_task = new_task("ship the release !2026-08-17")
    done_today_task = toggle_done(new_task("water the plants !2026-08-17"))
    other_day_task = new_task("buy bread !2026-08-18")

    result = due_today([due_today_task, done_today_task, other_day_task], today)

    assert result == [due_today_task]


def test_due_this_week_matches_the_glossary_definition():
    """@sdoc[REQ-FUNC-005]"""
    today = date(2026, 8, 17)
    within_week = new_task("ship the release !2026-08-23")  # exactly 6 days out
    outside_week = new_task("buy bread !2026-08-24")  # 7 days out, not this week

    result = due_this_week([within_week, outside_week], today)

    assert result == [within_week]


def test_overdue_matches_the_glossary_definition():
    """@sdoc[REQ-FUNC-005]"""
    today = date(2026, 8, 17)
    late_task = new_task("ship the release !2026-08-16")
    done_late_task = toggle_done(new_task("water the plants !2026-08-16"))
    future_task = new_task("buy bread !2026-08-18")

    result = overdue([late_task, done_late_task, future_task], today)

    assert result == [late_task]


def test_is_overdue_is_true_for_a_not_done_task_past_its_due_date():
    """@sdoc[REQ-FUNC-009]"""
    today = date(2026, 8, 17)
    task = new_task("ship the release !2026-08-16")

    assert is_overdue(task, today) is True


def test_is_overdue_is_false_for_a_done_task_past_its_due_date():
    """@sdoc[REQ-FUNC-009]"""
    today = date(2026, 8, 17)
    task = toggle_done(new_task("ship the release !2026-08-16"))

    assert is_overdue(task, today) is False


def test_is_overdue_is_false_for_a_task_with_no_due_date():
    """@sdoc[REQ-FUNC-009]"""
    today = date(2026, 8, 17)
    task = new_task("buy bread")

    assert is_overdue(task, today) is False


def test_is_overdue_is_false_for_a_task_due_today_or_later():
    """@sdoc[REQ-FUNC-009]"""
    today = date(2026, 8, 17)
    task = new_task("buy bread !2026-08-17")

    assert is_overdue(task, today) is False


def test_date_filters_are_deterministic():
    """@sdoc[REQ-FUNC-005]"""
    today = date(2026, 8, 17)
    tasks = [new_task("ship the release !2026-08-16")]

    assert overdue(tasks, today) == overdue(tasks, today)


def test_build_task_from_separate_field_values():
    """@sdoc[REQ-FUNC-006]"""
    task = build_task(text="buy bread", space="home", due_date="2026-08-20")

    assert task.text == "buy bread"
    assert task.space == "home"
    assert task.due_date == date(2026, 8, 20)


def test_build_task_with_an_empty_date_field_has_no_due_date():
    """@sdoc[REQ-FUNC-006]"""
    task = build_task(text="buy bread", space="", due_date="")

    assert task.due_date is None


def test_build_task_with_an_unparseable_date_field_has_no_due_date_but_still_builds():
    """@sdoc[REQ-FUNC-006]"""
    # a stray edit leaving garbage in the date field must never block creation
    task = build_task(text="buy bread", space="", due_date="not-a-date")

    assert task.text == "buy bread"
    assert task.due_date is None
