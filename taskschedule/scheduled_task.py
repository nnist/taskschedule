from datetime import datetime as dt
import json

from tasklib import Task
from isodate import parse_duration


class ScheduledTask():
    """A scheduled task."""

    def __init__(self, task: Task, schedule):
        self.schedule = schedule
        self.task: Task = task
        self.glyph = '○'
        self.active = task.active

        if task['status'] == 'completed':
            self.completed = True
        else:
            self.completed = False

        self.task_id = task['id']

        self.active_start = task['start']
        self.start = task['scheduled']
        self.start_time = '{}'.format(self.start.strftime('%H:%M'))

        try:
            estimate = task['estimate']
            duration = parse_duration(estimate)
            self.end = self.start + duration
        except TypeError:
            self.end = None

        try:
            self.timebox_estimate: int = task['tb_estimate']
            self.timebox_real: int = task['tb_real']
        except TypeError:
            pass

        self.description = task['description']

        self.project = task['project']

    @property
    def should_be_active(self):
        """Return true if the task should be active."""

        if self.start is not None:
            start_ts = dt.timestamp(self.start)
        else:
            start_ts = None

        now = dt.now()
        now_ts = dt.timestamp(now)

        if self.end is None:
            next_task = self.schedule.get_next_task(self)
            if next_task is not None:
                next_task_start_ts = dt.timestamp(next_task.start)
                if now_ts > start_ts and next_task_start_ts > now_ts:
                    return True
        else:
            end_ts = dt.timestamp(self.end)
            if now_ts > start_ts and end_ts > now_ts:
                return True

        return False

    @property
    def overdue(self):
        """If the task is overdue (current time is past end time),
           return True. Else, return False."""
        now = dt.now()
        now_ts = dt.timestamp(now)

        if self.end is None:
            start_ts = dt.timestamp(self.start)
            if now_ts > start_ts:
                return True

            return False

        end_ts = dt.timestamp(self.end)
        if now_ts > end_ts:
            return True

        return False

    def as_dict(self):
        data = self.task.export_data()
        return json.loads(data)
