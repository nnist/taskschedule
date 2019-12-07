from __future__ import annotations

from typing import TYPE_CHECKING

from taskschedule.main import Main
from taskschedule.utils import calculate_datetime

if TYPE_CHECKING:
    from datetime import datetime


class TestMain:
    def test_main_init_creates_backend_and_schedule(self, tw):
        main = Main(["-t", "tests/test-data/.taskrc", "--no-notifications"])

        backend = main.backend
        assert backend.taskrc_location == "tests/test-data/.taskrc"

        schedule = main.schedule
        assert schedule.backend is backend

    def test_main_command_args(self, tw):
        main = Main(["-t", "tests/test-data/.taskrc", "--no-notifications"])
        backend = main.backend
        task_command = backend.task_command
        assert "task" in task_command
        assert "status.not:deleted" in task_command

        scheduled_after: datetime = calculate_datetime("today-1s")
        scheduled_before: datetime = calculate_datetime("tomorrow")
        assert f"scheduled.after:{scheduled_after}" in task_command
        assert f"scheduled.before:{scheduled_before}" in task_command
