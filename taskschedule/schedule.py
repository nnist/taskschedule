"""This module provides a Schedule class, which is used for retrieving
   scheduled tasks from taskwarrior and displaying them in a table."""

import os
import datetime

from tasklib import TaskWarrior

from taskschedule.scheduled_task import (
    ScheduledTask,
    ScheduledTaskQuerySet,
    PatchedTaskWarrior,
)


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
        tw_data_dir=None,
        tw_data_dir_create=False,
        taskrc_location=None,
        scheduled_before=None,
        scheduled_after=None,
        scheduled="today",
        completed=True,
    ):
        home = os.path.expanduser("~")

        if tw_data_dir is None:
            tw_data_dir = home + "/.task"

        self.tw_data_dir = tw_data_dir

        if taskrc_location is None:
            taskrc_location = home + "/.taskrc"

        self.taskrc_location = taskrc_location

        self.tw_data_dir_create = tw_data_dir_create

        if os.path.isdir(self.tw_data_dir) is False:
            raise TaskDirDoesNotExistError(".task directory not found")

        if os.path.isfile(self.taskrc_location) is False:
            raise TaskrcDoesNotExistError(".taskrc not found")

        self.scheduled_before = scheduled_before
        self.scheduled_after = scheduled_after
        self.scheduled = scheduled
        self.completed = completed

        self.timeboxed_task: ScheduledTask = None
        self.tasks: ScheduledTaskQuerySet = self.get_tasks()

    def get_timebox_estimate_count(self):
        """"Return today's estimated timebox count."""
        total = 0
        for task in self.tasks:
            if task["tb_estimate"]:
                total += task["tb_estimate"]
        return total

    def get_timebox_real_count(self):
        """"Return today's real timebox count."""
        total = 0
        for task in self.tasks:
            if task["tb_real"]:
                total += task["tb_real"]
        return total

    def get_active_timeboxed_task(self):
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

    def get_tasks(self):
        """Retrieve scheduled tasks from taskwarrior."""
        taskwarrior = TaskWarrior(
            self.tw_data_dir,
            self.tw_data_dir_create,
            taskrc_location=self.taskrc_location,
        )

        # Disable _forcecolor because it breaks tw config output
        taskwarrior.overrides.update({"_forcecolor": "off"})

        if taskwarrior.config.get("uda.estimate.type") is None:
            raise UDADoesNotExistError(
                ("uda.estimate.type does not exist " "in .taskrc")
            )
        if taskwarrior.config.get("uda.estimate.label") is None:
            raise UDADoesNotExistError(
                ("uda.estimate.label does not exist " "in .taskrc")
            )

        task_command_args = ["task", "status.not:deleted"]

        if self.scheduled_before is not None and self.scheduled_after is not None:
            task_command_args.append(f"scheduled.after:{self.scheduled_after}")
            task_command_args.append(f"scheduled.before:{self.scheduled_before}")
        else:
            task_command_args.append(f"scheduled:{self.scheduled}")

        if not self.completed:
            task_command_args.append("status.not:completed")

        taskwarrior = PatchedTaskWarrior(
            self.tw_data_dir,
            self.tw_data_dir_create,
            taskrc_location=self.taskrc_location,
            task_command=" ".join(task_command_args),
        )
        queryset: ScheduledTaskQuerySet = ScheduledTaskQuerySet(backend=taskwarrior)

        self.tasks = queryset
        return self.tasks

    def load_tasks(self):
        """"Update the schedule's tasks. Return True if any tasks were updated,
            otherwise return False."""
        new_tasks = self.get_tasks()

        if self.tasks == new_tasks:
            return False

        self.tasks = new_tasks
        return True

    def get_calculated_date(self, synonym):
        """Leverage the `task calc` command to convert a date synonym string
           to a datetime object."""

        taskwarrior = TaskWarrior()
        task = ScheduledTask(taskwarrior, description="dummy")
        task["due"] = synonym
        return task["due"]

    def get_time_slots(self):
        """Return a dict with dates and their tasks.
        >>> get_time_slots()
        {datetime.date(2019, 6, 27): {00: [], 01: [], ..., 23: [task, task]},
         datetime.date(2019, 6, 28): {00: [], ..., 10: [task, task], ...}]
        """
        start_time = "0:00"
        end_time = "23:00"
        slot_time = 60

        start_date = self.get_calculated_date(self.scheduled_after)
        end_date = self.get_calculated_date(self.scheduled_before)
        scheduled_date = self.get_calculated_date(self.scheduled)

        if scheduled_date:
            start_date = scheduled_date.date()
            end_date = scheduled_date.date() + datetime.timedelta(hours=23, minutes=59)
        else:
            start_date = start_date.date()
            end_date = end_date.date()

        days = {}
        date = start_date
        while date <= end_date:
            hours = {}
            time = datetime.datetime.strptime(start_time, "%H:%M")
            end = datetime.datetime.strptime(end_time, "%H:%M")
            while time <= end:
                task_list = []
                for task in self.tasks:
                    start = task["scheduled"]
                    if start.date() == date:
                        if start.hour == int(time.strftime("%H")):
                            task_list.append(task)

                task_list = sorted(task_list, key=lambda k: k["scheduled"])
                hours[time.strftime("%H")] = task_list
                time += datetime.timedelta(minutes=slot_time)
            days[date.isoformat()] = hours
            date += datetime.timedelta(days=1)

        return days

    def get_max_length(self, value):
        """Return the max string length of a given value of all tasks
           in the schedule.
        """
        max_length = 0
        for task in self.tasks:
            length = len(str(task[value]))
            if length > max_length:
                max_length = length

        return max_length

    def get_column_offsets(self):
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

    def get_next_task(self, task):
        """Get the next scheduled task after the given task. If there is no
           next scheduled task, return None."""
        next_tasks = []
        for task_ in self.tasks:
            if task_.start > task.start:
                next_tasks.append(task_)

        next_tasks.sort(key=lambda task: task.start)

        if next_tasks:
            return next_tasks[0]

        return None

    def align_matrix(self, array):
        """Align all columns in a matrix by padding the items with spaces.
           Return the aligned array."""
        col_sizes = {}
        for row in array:
            for i, col in enumerate(row):
                col_sizes[i] = max(col_sizes.get(i, 0), len(col))

        ncols = len(col_sizes)
        result = []
        for row in array:
            row = list(row) + [""] * (ncols - len(row))
            for i, col in enumerate(row):
                row[i] = col.ljust(col_sizes[i])

            result.append(row)

        return result
