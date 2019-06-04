from datetime import datetime as dt

from isodate import parse_duration


class ScheduledTask():
    """A scheduled task."""
    def __init__(self, task):
        self.task = task
        self.glyph = '○'
        self.active = task.active

        if task['status'] == 'completed':
            self.completed = True
        else:
            self.completed = False

        try:
            self.task_id = task['id']
        except TypeError:
            self.task_id = 0

        try:
            self.start = task['scheduled']
            self.start_time = '{}'.format(self.start.strftime('%H:%M'))
        except TypeError:
            self.start = None
            self.start_time = None

        try:
            estimate = task['estimate']
            duration = parse_duration(estimate)
            self.end = self.start + duration
        except TypeError:
            self.end = None

        try:
            self.description = task['description']
        except TypeError:
            self.description = None

        try:
            self.project = task['project']
        except TypeError:
            self.project = None

    def should_be_active(self, next_task):
        """If the task should be active (current time is past scheduled time
           but before end time), return True. Else, return False."""
        if self.start is not None:
            start_ts = dt.timestamp(self.start)
        else:
            start_ts = None

        now = dt.now()
        now_ts = dt.timestamp(now)
        if self.start is None:
            next_task_start_ts = dt.timestamp(next_task.start)
            if now_ts > start_ts and next_task_start_ts > now_ts:
                return True
        else:
            if self.end is None:
                return False

            end_ts = dt.timestamp(self.end)
            if now_ts > start_ts and end_ts > now_ts:
                return True

        return False
