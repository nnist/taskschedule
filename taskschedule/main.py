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

    previous_lines = []

    while True:
        max_y, max_x = stdscr.getmaxyx()

        schedule.get_tasks(scheduled=scheduled, completed=completed)

        as_dict = schedule.as_dict()

        lines = [['', '', 'ID', 'Time', 'Description']]
        past_first_task = False
        line_with_last_task = 0

        # Fill lines with tasks
        for i in range(24):
            tasks = as_dict[i]
            if not tasks:
                # Add empty line if between tasks or option is enabled
                if past_first_task or not hide_empty:
                    lines.append([str(i), '', '', '', ''])
            else:
                past_first_task = True
                for task in tasks:
                    color = curses.color_pair(1)
                    hour = task['scheduled'].hour
                    glyph = '○'
                    task_id = task['id']
                    start = task['scheduled']
                    estimate = task['estimate']
                    start_time = '{}'.format(start.strftime('%H:%M'))
                    description = task['description']

                    if estimate is None:
                        formatted_time = '{}'.format(start_time)
                    else:
                        duration = parse_duration(estimate)
                        end = start + duration
                        end_time = '{}'.format(end.strftime('%H:%M'))
                        formatted_time = '{}-{}'.format(start_time, end_time)

                    line = [str(hour), glyph, str(task_id),
                            formatted_time, description]
                    lines.append(line)
                    line_with_last_task = len(lines)

        # Optionally truncate empty lines after last task
        if hide_empty:
            lines = lines[0:line_with_last_task]

        # Clear the screen if lines have changed since last time
        if lines != previous_lines:
            stdscr.clear()
        previous_lines = lines

        # Align the lines
        matrix = schedule.align_matrix(lines)

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

            # Draw time if row is not empty
            if task_id == ' ' * len(row[2]):
                formatted_time = ' ' * len(row[3])
            else:
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
