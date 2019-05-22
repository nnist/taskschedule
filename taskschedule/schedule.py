"""This module provides a Schedule class, which is used for retrieving
   scheduled tasks from taskwarrior and displaying them in a table."""

from operator import itemgetter

from tabulate import tabulate
from tasklib import TaskWarrior
from isodate import parse_duration

class Schedule():
    """This class provides methods to format tasks and display them in
       a schedule report."""
    def __init__(self, tw_data_dir='~/.task', tw_data_dir_create=False):
        self.tw_data_dir = tw_data_dir
        self.tw_data_dir_create = tw_data_dir_create
        self.tasks = []

    def get_tasks(self):
        """Retrieve today's scheduled tasks from taskwarrior."""
        taskwarrior = TaskWarrior(self.tw_data_dir, self.tw_data_dir_create)
        self.tasks = taskwarrior.tasks.filter(scheduled='today',
                                              status='pending')

    def format_task(self, task):
        """Format a task. Put the details in a list and return it."""
        hour = task['scheduled'].hour
        glyph = '○'
        task_id = task['id']

        start = task['scheduled']
        estimate = task['estimate']

        start_time = '{}'.format(start.strftime('%H:%M'))

        if estimate is None:
            formatted_time = '{}'.format(start_time)
        else:
            duration = parse_duration(estimate)
            end = start + duration
            end_time = '{}'.format(end.strftime('%H:%M'))
            formatted_time = '{}-{}'.format(start_time, end_time)

        description = task['description']

        formatted_task = [hour, glyph, task_id, formatted_time, description]
        return formatted_task

    def format_as_table(self, hide_empty=True):
        """Format the scheduled tasks as a table. If hide_empty is True,
           hide all unused hours. Return the table as a string."""
        tasks = self.tasks
        formatted_tasks = []

        for task in tasks:
            formatted_task = self.format_task(task)
            formatted_tasks.append(formatted_task)

        hours = []
        for task in formatted_tasks:
            hours.append(task[0])

        first_hour = 0
        if hide_empty:
            try:
                first_hour = sorted(hours)[0]
            except IndexError:
                pass

        last_hour = 23
        if hide_empty:
            try:
                last_hour = sorted(hours)[-1]
            except IndexError:
                pass

        # Fill remaining hours on schedule with empty lines
        for i in range(24):
            if i > first_hour - 2 and i < last_hour + 2:
                if i not in hours:
                    formatted_tasks.append([i, '', '', '', ''])

        sorted_tasks = sorted(formatted_tasks, key=itemgetter(0))

        headers = ['', '', 'ID', 'Time', 'Description']
        return tabulate(sorted_tasks, headers, tablefmt="plain")
