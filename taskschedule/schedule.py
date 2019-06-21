"""This module provides a Schedule class, which is used for retrieving
   scheduled tasks from taskwarrior and displaying them in a table."""

import os

from tasklib import TaskWarrior

from taskschedule.scheduled_task import ScheduledTask


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


class Schedule():
    """This class provides methods to format tasks and display them in
       a schedule report."""
    def __init__(self, tw_data_dir='~/.task', tw_data_dir_create=False,
                 taskrc_location='~/.taskrc'):
        self.tw_data_dir = tw_data_dir
        self.tw_data_dir_create = tw_data_dir_create
        self.taskrc_location = taskrc_location
        self.tasks = []

        if os.path.isdir(self.tw_data_dir) is False:
            raise TaskDirDoesNotExistError('.task directory not found')

        if os.path.isfile(self.taskrc_location) is False:
            raise TaskrcDoesNotExistError('.taskrc not found')

    def load_tasks(self, scheduled_before=None, scheduled_after=None,
                   scheduled='today', completed=True):
        """Retrieve today's scheduled tasks from taskwarrior."""
        taskwarrior = TaskWarrior(self.tw_data_dir, self.tw_data_dir_create,
                                  taskrc_location=self.taskrc_location)

        # Disable _forcecolor because it breaks tw config output
        taskwarrior.overrides.update({'_forcecolor': 'off'})
        if taskwarrior.config.get('uda.estimate.type') is None:
            raise UDADoesNotExistError(('uda.estimate.type does not exist '
                                        'in .taskrc'))
        if taskwarrior.config.get('uda.estimate.label') is None:
            raise UDADoesNotExistError(('uda.estimate.label does not exist '
                                        'in .taskrc'))

        scheduled_tasks = []
        filtered_tasks = []

        if scheduled_before is not None and scheduled_after is not None:
            filtered_tasks.extend(taskwarrior.tasks.filter(
                scheduled__before=scheduled_before,
                scheduled__after=scheduled_after,
                status='pending'))

            if completed:
                filtered_tasks.extend(taskwarrior.tasks.filter(
                    scheduled__before=scheduled_before,
                    scheduled__after=scheduled_after,
                    status='completed'))
        else:
            filtered_tasks.extend(taskwarrior.tasks.filter(
                scheduled=scheduled,
                status='pending'))

            if completed:
                filtered_tasks.extend(taskwarrior.tasks.filter(
                    scheduled=scheduled,
                    status='completed'))

        for task in filtered_tasks:
            scheduled_task = ScheduledTask(task, self)
            scheduled_tasks.append(scheduled_task)

        scheduled_tasks.sort(key=lambda task: task.start)
        self.tasks = scheduled_tasks

    def as_dict(self):
        """Return a dict with scheduled tasks.
        >>> as_dict()
        {1: [], 2: [], ..., 9: [task, task, task], 10: [task, task], ...}
        """
        as_dict = {}
        for i in range(24):
            task_list = []
            for task in self.tasks:
                start = task.start
                if start.hour == i:
                    task_list.append(task)

            task_list = sorted(task_list, key=lambda k: k.start)
            as_dict[i] = task_list

        return as_dict

    def get_max_length(self, value):
        """Return the max string length of a given value of all tasks
           in the schedule.
        """
        max_length = 0
        for task in self.tasks:
            length = len(str(task.task[value]))
            if length > max_length:
                max_length = length

        return max_length

    def get_column_offsets(self):
        """Return the offsets for each column in the schedule for rendering
           a table."""
        offsets = [0, 5]  # Hour, glyph
        offsets.append(5 + self.get_max_length('id') + 1)  # ID
        offsets.append(offsets[2] + 12)  # Time

        add_offset = self.get_max_length('project') + 1

        if add_offset < 8:
            add_offset = 8

        offsets.append(offsets[3] + add_offset)  # Project
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
            row = list(row) + [''] * (ncols - len(row))
            for i, col in enumerate(row):
                row[i] = col.ljust(col_sizes[i])

            result.append(row)

        return result
