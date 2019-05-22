import sys
import os
import argparse
import time
import curses
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

        headers = ['', '', 'ID', 'Time', 'Description']
        return tabulate(sorted_tasks, headers, tablefmt="plain")


def draw(stdscr, refresh_rate=1):
    schedule = Schedule()
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, 8, 0)

    while True:
        stdscr.clear()

        schedule.get_tasks()
        rows = schedule.format_as_table().splitlines()
        header = rows[0]
        data = rows[1:]

        stdscr.addstr(0, 0, header, curses.color_pair(1) | curses.A_UNDERLINE)

        for i, row in enumerate(data):
            stdscr.addstr(i+1, 0, row[:2], curses.color_pair(2))
            stdscr.addstr(i+1, 2, row[2:], curses.color_pair(1))

        stdscr.refresh()
        time.sleep(refresh_rate)


def main(argv):
    """Display a schedule report for taskwarrior."""
    parser = argparse.ArgumentParser(
        description="""Display a schedule report for taskwarrior."""
    )
    parser.add_argument(
        '-r', '--refresh', help="refresh every n seconds", type=int, default=1
    )
    args = parser.parse_args(argv)

    curses.wrapper(draw, args.refresh)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print('Interrupted by user.')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0) # pylint: disable=protected-access
