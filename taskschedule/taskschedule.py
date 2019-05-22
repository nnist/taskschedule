from operator import itemgetter

from tabulate import tabulate
from tasklib import TaskWarrior
from isodate import parse_duration

class Schedule():
    def __init__(self, tw_data_dir='~/.task', tw_data_dir_create=False):
        self.tw_data_dir = tw_data_dir
        self.tw_data_dir_create = tw_data_dir_create
        self.tasks = []

    def get_tasks(self):
        taskwarrior = TaskWarrior(self.tw_data_dir, self.tw_data_dir_create)
        self.tasks = taskwarrior.tasks.filter(scheduled='today',
                                              status='pending')

    def format_task(self, task):
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

    def format_as_table(self):
        tasks = self.tasks
        formatted_tasks = []

        for task in tasks:
            formatted_task = self.format_task(task)
            formatted_tasks.append(formatted_task)

        hours = []
        for task in formatted_tasks:
            hours.append(task[0])

        for i in range(24):
            if i not in hours:
                formatted_tasks.append([i, '', '', '', ''])

        sorted_tasks = sorted(formatted_tasks, key=itemgetter(0))

        headers = ['', '', '\033[4mID\033[0m', '\033[4mTime\033[0m',
                   '\033[4mDescription\033[0m']
        return tabulate(sorted_tasks, headers, tablefmt="plain")
