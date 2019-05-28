"""This module provides a Schedule class, which is used for retrieving
   scheduled tasks from taskwarrior and displaying them in a table."""

from tasklib import TaskWarrior


class Schedule():
    """This class provides methods to format tasks and display them in
       a schedule report."""
    def __init__(self, tw_data_dir='~/.task', tw_data_dir_create=False):
        self.tw_data_dir = tw_data_dir
        self.tw_data_dir_create = tw_data_dir_create
        self.tasks = []

    def get_tasks(self, scheduled='today', completed=True):
        """Retrieve today's scheduled tasks from taskwarrior."""
        taskwarrior = TaskWarrior(self.tw_data_dir, self.tw_data_dir_create)
        tasks = []
        for task in taskwarrior.tasks.filter(scheduled=scheduled, status='pending'):
            tasks.append(task)

        if completed:
            for task in taskwarrior.tasks.filter(scheduled=scheduled, status='completed'):
                tasks.append(task)

        self.tasks = tasks

    def as_dict(self):
        """Return a dict with scheduled tasks.
        >>> as_dict()
        {1: [], 2: [], ..., 9: [task, task, task], 10: [task, task], ...}
        """
        as_dict = {}
        for i in range(24):
            task_list = []
            for task in self.tasks:
                start = task['scheduled']
                if start.hour == i:
                    task_list.append(task)

            task_list = sorted(task_list, key=lambda k: k['scheduled'])
            as_dict[i] = task_list

        return as_dict

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
