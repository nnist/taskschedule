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
    def scheduled_end_time(self) -> Optional[dt]:
        """Return the task's end datetime."""
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

        if self["scheduled"] is None:
            return False

        start_ts: float = dt.timestamp(self["scheduled"])

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
        now = dt.now()
        now_ts = dt.timestamp(now)

        if self["end"] is None:
            start_ts = dt.timestamp(self["scheduled"])
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
