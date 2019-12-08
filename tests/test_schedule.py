from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING

import pytest

from taskschedule.schedule import Day, Hour
from taskschedule.utils import calculate_datetime

if TYPE_CHECKING:
    from taskschedule.schedule import Schedule


class TestSchedule:
    def test_get_tasks_returns_correct_tasks(self, schedule: Schedule):
        tasks = schedule.tasks
        assert len(tasks) == 8
        assert tasks[0]["description"] == "test_last_week"
        assert tasks[1]["description"] == "test_yesterday"
        assert tasks[2]["description"] == "test_0:00"
        assert tasks[3]["description"] == "test_9:00_to_10:11"
        assert tasks[4]["description"] == "test_14:00_to_16:00"
        assert tasks[5]["description"] == "test_16:10_to_16:34"
        assert tasks[6]["description"] == "test_tomorrow"
        assert tasks[7]["description"] == "test_next_week"

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
            assert next_task["description"] == "test_9:00_to_10:11"
        else:
            pytest.fail("A next task was expected but not returned.")

    def test_get_next_task_for_last_task_returns_none(self, schedule: Schedule):
        next_task = schedule.get_next_task(schedule.tasks[7])
        assert not next_task

    def test_days(self, schedule: Schedule):
        days = schedule.days
        assert len(days[2].tasks) == 4
        assert days[2].tasks[0]["description"] == "test_0:00"
        assert days[2].tasks[1]["description"] == "test_9:00_to_10:11"
        assert days[2].tasks[2]["description"] == "test_14:00_to_16:00"
        assert days[2].tasks[3]["description"] == "test_16:10_to_16:34"


class TestDay:
    def test_day_only_returns_tasks_for_day(self, schedule: Schedule):
        date = dt.datetime.now().date()
        day = Day(date, schedule.tasks)
        assert len(day.tasks) == 4
        assert day.tasks[0]["description"] == "test_0:00"
        assert day.tasks[1]["description"] == "test_9:00_to_10:11"
        assert day.tasks[2]["description"] == "test_14:00_to_16:00"
        assert day.tasks[3]["description"] == "test_16:10_to_16:34"

    def test_day_has_tasks(self, schedule: Schedule):
        date = dt.datetime.now().date()
        day = Day(date, schedule.tasks)
        assert day.has_tasks

        day = Day(date, schedule.tasks.filter("scheduled:tomorrow+50days"))
        assert not day.has_tasks

    def test_hours(self, schedule: Schedule):
        date = dt.datetime.now().date()
        day = Day(date, schedule.tasks)
        hours = day.hours
        assert len(hours) == 24
        assert hours[9].tasks[0]["description"] == "test_9:00_to_10:11"
        assert hours[14].tasks[0]["description"] == "test_14:00_to_16:00"
        assert hours[16].tasks[0]["description"] == "test_16:10_to_16:34"


class TestHour:
    def test_hour_has_tasks(self, schedule: Schedule):
        hour = Hour(9, schedule.tasks[0])
        assert hour.has_tasks

        hour = Hour(9, schedule.tasks.filter("scheduled:tomorrow+50days"))
        assert not hour.has_tasks
