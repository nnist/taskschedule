from tabulate import tabulate
from tasklib import Task, TaskWarrior


class Schedule():
    def __init__(self):
        self.tasks = []

    def get_tasks(self):
        taskwarrior = TaskWarrior(data_location='~/.task', create=False)
        self.tasks = taskwarrior.tasks.filter(scheduled='today')

    def print_as_table(self):
        rows = []

        # TODO Sort tasks by hour
        sorted_tasks = self.tasks

        # TODO Fill in remaining hours with empty lines

        for task in sorted_tasks:
            hour = task['scheduled'].hour
            glyph = '○'
            task_id = task['id']

            # TODO Improve time formatting
            start = '{}:{}'.format(task['scheduled'].hour, task['scheduled'].minute)
            end = '{}:{}'.format(task['scheduled'].hour, task['scheduled'].minute)
            time = '{}-{}'.format(start, end)

            description = task['description']
            rows.append([hour, glyph, task_id, time, description])

        headers = ['', '', '\033[4mID\033[0m', '\033[4mTime\033[0m',
                   '\033[4mDescription\033[0m']
        print(tabulate(rows, headers, tablefmt="plain"))


schedule = Schedule()
schedule.get_tasks()
schedule.print_as_table()
