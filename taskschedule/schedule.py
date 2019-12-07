"""This module provides a Schedule class, which is used for retrieving
   scheduled tasks from taskwarrior and displaying them in a table."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from cached_property import cached_property

from taskschedule.scheduled_task import ScheduledTask, ScheduledTaskQuerySet
from taskschedule.taskwarrior import PatchedTaskWarrior


class UDADoesNotExistError(Exception):
    """Raised when UDA is not found in .taskrc file."""

    # pylint: disable=unnecessary-pass
    pass


class TaskrcDoesNotExistError(Exception):
    """Raised when the .taskrc file has not been found."""

    # pylint: disable=unnecessary-pass
    pass


class TaskDirDoesNotExistError(Exception):
    """Raised when the .task directory has not been found."""

    # pylint: disable=unnecessary-pass
    pass


class Schedule:
    """This class provides methods to format tasks and display them in
       a schedule report."""

    def __init__(
        self,
        backend: PatchedTaskWarrior,
        scheduled_after: datetime,
        scheduled_before: datetime,
    ):
        self.backend = backend

        self.scheduled_before = scheduled_before
        self.scheduled_after = scheduled_after

        self.timeboxed_task: Optional[ScheduledTask] = None

    def get_timebox_estimate_count(self) -> int:
        """"Return today's estimated timebox count."""
        total = 0
        for task in self.tasks:
            if task["tb_estimate"]:
                total += task["tb_estimate"]
        return total

    def get_timebox_real_count(self) -> int:
        """"Return today's real timebox count."""
        total = 0
        for task in self.tasks:
            if task["tb_real"]:
                total += task["tb_real"]
        return total

    def get_active_timeboxed_task(self) -> Optional[ScheduledTask]:
        """If a timeboxed task is currently active, return it. Otherwise,
           return None."""
        for task in self.tasks:
            if task.active and task["tb_estimate"]:
                self.timeboxed_task = task

        if self.timeboxed_task:
            return self.timeboxed_task

        return None

    def stop_active_timeboxed_task(self):
        """Stop the current timeboxed task."""
        timeboxed_task = self.get_active_timeboxed_task()
        timeboxed_task.stop()
        self.timeboxed_task = None

    def clear_cache(self):
        """Clear the scheduled tasks cache."""
        if self.tasks:
            del self.__dict__["tasks"]

    @cached_property
    def tasks(self) -> ScheduledTaskQuerySet:
        """Retrieve scheduled tasks from taskwarrior."""
        queryset: ScheduledTaskQuerySet = ScheduledTaskQuerySet(backend=self.backend)

        return queryset

    def get_time_slots(self) -> Dict:
        """Return a dict with dates and their tasks.
        >>> get_time_slots()
        {datetime.date(2019, 6, 27): {00: [], 01: [], ..., 23: [task, task]},
         datetime.date(2019, 6, 28): {00: [], ..., 10: [task, task], ...}]
        """
        start_time = "0:00"
        end_time = "23:00"
        slot_time = 60

        start_date = self.scheduled_after.date()
        end_date = self.scheduled_before.date()

        days = {}
        date = start_date
        while date <= end_date:
            hours = {}
            time = datetime.strptime(start_time, "%H:%M")
            end = datetime.strptime(end_time, "%H:%M")
            while time <= end:
                task_list = []
                task: ScheduledTask
                for task in self.tasks:
                    start = task.scheduled_start_datetime
                    if start and start.date() == date:
                        if start.hour == int(time.strftime("%H")):
                            task_list.append(task)

                task_list = sorted(task_list, key=lambda k: k["scheduled"])
                hours[time.strftime("%H")] = task_list
                time += timedelta(minutes=slot_time)
            days[date.isoformat()] = hours
            date += timedelta(days=1)

        return days

    def get_max_length(self, key: str) -> int:
        """Return the max string length of a given key's value of all tasks
           in the schedule. Useful for determining column widths.
        """
        max_length = 0
        for task in self.tasks:
            length = len(str(task[key]))
            if length > max_length:
                max_length = length

        return max_length

    def get_column_offsets(self) -> List[int]:
        """Return the offsets for each column in the schedule for rendering
           a table."""
        offsets = [0, 5]  # Hour, glyph
        offsets.append(5 + self.get_max_length("id") + 1)  # ID
        offsets.append(offsets[2] + 12)  # Time
        offsets.append(offsets[3] + 10)  # Timeboxes

        add_offset = self.get_max_length("project") + 1

        if add_offset < 8:
            add_offset = 8

        offsets.append(offsets[4] + add_offset)  # Project
        return offsets

    def get_next_task(self, task: ScheduledTask) -> Optional[ScheduledTask]:
        """Get the next scheduled task after the given task. If there is no
           next scheduled task, return None."""
        next_tasks = []
        for task_ in self.tasks:
            if task_.scheduled_start_datetime > task.scheduled_start_datetime:
                next_tasks.append(task_)

        next_tasks.sort(key=lambda task: task.scheduled_start_datetime)

        if next_tasks:
            return next_tasks[0]

        return None
