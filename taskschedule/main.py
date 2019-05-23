"""Command line interface of taskschedule"""

import time
import curses
import argparse

from taskschedule.schedule import Schedule

from isodate import parse_duration


def draw(stdscr, refresh_rate=1, hide_empty=True, scheduled='today', completed=True):
    """Draw the schedule using curses."""
    schedule = Schedule()
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, 20, curses.COLOR_BLACK)
    curses.init_pair(2, 8, 0)  # Hours
    curses.init_pair(3, 20, 234)  # Alternating background
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Header
    curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Current hour
    curses.init_pair(6, 19, 234)  # Completed task - alternating background
    curses.init_pair(7, 19, 0)  # Completed task

    while True:
        max_y, max_x = stdscr.getmaxyx()

        stdscr.clear()

        schedule.get_tasks(scheduled=scheduled, completed=completed)
        tasks = schedule.tasks

        # Create matrix with tasks
        formatted_tasks = [['', '', 'ID', 'Time', 'Description']]
        for task in tasks:
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

            formatted_task = [str(hour), glyph, str(task_id), formatted_time,
                              description]
            formatted_tasks.append(formatted_task)

        # Create list of hours that have tasks
        hours = []
        for task in formatted_tasks[1:]:
            hours.append(int(task[0]))

        # Determine first scheduled hour
        first_hour = 0
        if hide_empty:
            try:
                first_hour = sorted(hours)[0]
            except IndexError:
                pass

        # Determine last scheduled hour
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
                    formatted_tasks.append([str(i), '', '', '', ''])

        # Align the formatted tasks
        matrix = schedule.align_matrix(formatted_tasks)

        # Sort the matrix by hour
        matrix[1:] = sorted(matrix[1:], key=lambda k: int(k[0]))

        # Draw header
        header = ' '.join(matrix[0])
        for i, char in enumerate(header):
            if char == ' ':
                color = curses.color_pair(1)
            else:
                color = curses.color_pair(4) | curses.A_UNDERLINE
            stdscr.addstr(0, i, char, color)

        # Draw schedule
        for i, row in enumerate(matrix[1:]):
            offset = 0
            color = curses.color_pair(1)

            # Draw hours, highlight current hour
            current_hour = time.localtime().tm_hour
            hour = row[0]
            if int(hour) == current_hour:
                color = curses.color_pair(5)
            else:
                color = curses.color_pair(2)

            stdscr.addstr(i+1, offset, hour, color)
            offset += 3

            # Draw glyph
            color = curses.color_pair(1)
            glyph = row[1]
            stdscr.addstr(i+1, offset, glyph, color)
            offset += len(glyph) + 1

            # Set color using alternating background
            if i % 2:
                if str(row[2]).startswith('0'):
                    color = curses.color_pair(7)
                else:
                    color = curses.color_pair(1)
            else:
                if str(row[2]).startswith('0'):
                    color = curses.color_pair(6)
                else:
                    color = curses.color_pair(3)

            # Draw ID
            task_id = row[2]
            stdscr.addstr(i+1, offset, task_id + ' ', color)
            offset += len(task_id) + 1

            # Draw time
            formatted_time = row[3]
            stdscr.addstr(i+1, offset, formatted_time + ' ', color)
            offset += len(formatted_time) + 1

            # Draw description
            description = row[4]
            stdscr.addstr(i+1, offset, description, color)

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
    parser.add_argument(
        '-s', '--scheduled', help="scheduled date: ex. 'today', 'tomorrow'",
        type=str, default='today'
    )
    parser.add_argument(
        '-a', '--all', help="show all hours, even if empty",
        action='store_true', default=False
    )
    parser.add_argument(
        '-c', '--completed', help="hide completed tasks",
        action='store_false', default=True
    )
    args = parser.parse_args(argv)

    hide_empty = not args.all
    curses.wrapper(draw, args.refresh, hide_empty, args.scheduled, args.completed)
