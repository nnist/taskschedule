import json
import os
import tempfile
from datetime import datetime as dt
from typing import Dict, Optional

from isodate import parse_duration
from tasklib.task import Task, TaskQuerySet


class ScheduledTaskQuerySet(TaskQuerySet):
    ...


class ScheduledTask(Task):
    """A scheduled task."""

    def __init__(self, *args, **kwargs):
        super(ScheduledTask, self).__init__(*args, **kwargs)
        # TODO Create reference to Schedule
        self.glyph = "○"

    @property
    def has_scheduled_time(self) -> bool:
        """If task's scheduled time is 00:00:00, it has been scheduled for a
           particular day but not for a specific time. If this is the case,
           return False."""
        start = self.scheduled_start_datetime
        if start:
            if (
                start.hour == 0
                and start.minute == 0
                and start.second == 0
                and start.microsecond == 0
            ):
                return False
            else:
                return True

        return False

    @property
    def scheduled_start_datetime(self) -> Optional[dt]:
        """Return the task's scheduled start datetime."""
        try:
            return self["scheduled"]
        except TypeError:
            return None

    @property
    def scheduled_end_datetime(self) -> Optional[dt]:
        """Return the task's scheduled end datetime."""
        try:
            estimate: dt = self["estimate"]
            duration = parse_duration(estimate)
            return self["scheduled"] + duration
        except TypeError:
            return None

    @property
    def notified(self) -> bool:
        filename = tempfile.gettempdir() + "/taskschedule"

        if os.path.exists(filename):
            append_write = "r+"
        else:
            append_write = "w+"

        with open(filename, append_write) as file_:
            uuid = self["uuid"]
            if uuid not in str(file_.readlines()):
                file_.write(f"{uuid},")
                return False

        return True

    @property
    def should_be_active(self) -> bool:
        """Return true if the task should be active."""

        if self.scheduled_start_datetime is None:
            return False

        start_ts: float = dt.timestamp(self.scheduled_start_datetime)

        now = dt.now()
        now_ts = dt.timestamp(now)

        if self["end"] is None:
            # TODO Implement get_next_task differently
            # next_task = self.schedule.get_next_task(self)
            next_task = None
            if next_task is not None:
                next_task_start_ts = dt.timestamp(next_task.start)
                if now_ts > start_ts and next_task_start_ts > now_ts:
                    return True
        else:
            end_ts = dt.timestamp(self["end"])
            if now_ts > start_ts and end_ts > now_ts:
                return True

        return False

    @property
    def overdue(self) -> bool:
        """If the task is overdue (current time is past end time),
           return True. Else, return False."""
        if not self.scheduled_start_datetime:
            return False

        now = dt.now()
        now_ts = dt.timestamp(now)

        if self["end"] is None:
            start_ts = dt.timestamp(self.scheduled_start_datetime)
            if now_ts > start_ts:
                return True

            return False

        end_ts = dt.timestamp(self["end"])
        if now_ts > end_ts:
            return True

        return False

    def as_dict(self) -> Dict:
        data = self.export_data()
        return json.loads(data)
