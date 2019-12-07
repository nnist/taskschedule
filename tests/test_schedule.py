from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from taskschedule.utils import calculate_datetime

if TYPE_CHECKING:
    from taskschedule.schedule import Schedule


class TestSchedule:
    def test_get_tasks_returns_correct_tasks(self, schedule: Schedule):
        tasks = schedule.tasks
        assert len(tasks) == 7
        assert tasks[0]["description"] == "test_last_week"
        assert tasks[1]["description"] == "test_yesterday"
        assert tasks[2]["description"] == "test_9:00_to_10:11"
        assert tasks[3]["description"] == "test_14:00_to_16:00"
        assert tasks[4]["description"] == "test_16:10_to_16:34"
        assert tasks[5]["description"] == "test_tomorrow"
        assert tasks[6]["description"] == "test_next_week"

    def test_clear_cache(self, schedule: Schedule):
        tasks = schedule.tasks
        assert tasks
        schedule.clear_cache()
        with pytest.raises(KeyError):
            schedule.__dict__["tasks"]

        tasks = schedule.tasks
        assert tasks

    def test_get_time_slots_returns_correct_amount_of_days(self, schedule: Schedule):
        time_slots = schedule.get_time_slots()
        assert len(time_slots) == 7

    def test_get_time_slots_has_correct_tasks(self, schedule: Schedule):
        time_slots = schedule.get_time_slots()

        yesterday = calculate_datetime("yesterday").date().isoformat()
        today = calculate_datetime("today").date().isoformat()
        tomorrow = calculate_datetime("tomorrow").date().isoformat()

        assert time_slots[yesterday]["00"][0]["description"] == "test_yesterday"
        assert time_slots[today]["09"][0]["description"] == "test_9:00_to_10:11"
        assert time_slots[today]["14"][0]["description"] == "test_14:00_to_16:00"
        assert time_slots[today]["16"][0]["description"] == "test_16:10_to_16:34"
        assert time_slots[tomorrow]["00"][0]["description"] == "test_tomorrow"

    def test_get_max_length(self, schedule: Schedule):
        length = schedule.get_max_length("description")
        assert length == 19

    def test_get_column_offsets(self, schedule: Schedule):
        offsets = schedule.get_column_offsets()
        assert offsets == [0, 5, 7, 19, 29, 37]

    def test_get_next_task_returns_next_task(self, schedule: Schedule):
        next_task = schedule.get_next_task(schedule.tasks[2])
        if next_task:
            assert next_task["description"] == "test_14:00_to_16:00"
        else:
            pytest.fail("A next task was expected but not returned.")

    def test_get_next_task_for_last_task_returns_none(self, schedule: Schedule):
        next_task = schedule.get_next_task(schedule.tasks[6])
        assert not next_task
