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
    curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_GREEN)  # Active task
    curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_BLACK)  # Glyph

    previous_as_dict = []

    while True:
        max_y, max_x = stdscr.getmaxyx()

        schedule.get_tasks(scheduled=scheduled, completed=completed)

        as_dict = schedule.as_dict()

        # Clear the screen if lines have changed since last time
        if as_dict != previous_as_dict:
            stdscr.clear()
        previous_as_dict = as_dict

        # Draw header
        headers = ['', '', 'ID', 'Time', 'Description']
        color = curses.color_pair(4) | curses.A_UNDERLINE
        offset = 5
        stdscr.addstr(0, offset, headers[2], color)
        offset = 5 + schedule.get_max_length('id') + 1
        stdscr.addstr(0, offset, headers[3], color)
        offset += 12
        stdscr.addstr(0, offset, headers[4], color)

        # Draw schedule
        past_first_task = False
        alternate = True
        current_line = 1
        for i in range(24):
            tasks = as_dict[i]
            if not tasks:
                # Add empty line if between tasks or option is enabled
                if past_first_task or not hide_empty:
                    if alternate:
                        color = curses.color_pair(1)
                    else:
                        color = curses.color_pair(3)

                    # Fill line to screen length
                    stdscr.addstr(current_line, 5, ' ' * (max_x - 5), color)

                    # Draw hour, highlight current hour
                    current_hour = time.localtime().tm_hour
                    if i == current_hour:
                        stdscr.addstr(current_line, 0, str(i),
                                      curses.color_pair(5))
                    else:
                        stdscr.addstr(current_line, 0, str(i),
                                      curses.color_pair(2))

                    current_line += 1
                    alternate = not alternate

            for ii, task in enumerate(tasks):
                past_first_task = True
                if task.active:
                    color = curses.color_pair(8)
                else:
                    if alternate:
                        if task['status'] == 'completed':
                            color = curses.color_pair(7)
                        else:
                            color = curses.color_pair(1)
                    else:
                        if task['status'] == 'completed':
                            color = curses.color_pair(6)
                        else:
                            color = curses.color_pair(3)

                # Only draw hour once for multiple tasks
                if ii == 0:
                    hour = str(i)
                else:
                    hour = ''

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

                # Draw hour, highlight current hour
                current_hour = time.localtime().tm_hour
                if hour != '':
                    if int(hour) == current_hour:
                        stdscr.addstr(current_line, 0, hour,
                                      curses.color_pair(5))
                    else:
                        stdscr.addstr(current_line, 0, hour,
                                      curses.color_pair(2))

                # Fill line to screen length
                stdscr.addstr(current_line, 5, ' ' * (max_x - 5), color)

                # Draw task details
                stdscr.addstr(current_line, 3, glyph, curses.color_pair(9))
                stdscr.addstr(current_line, 5, str(task_id), color)
                offset = 5 + schedule.get_max_length('id') + 1
                stdscr.addstr(current_line, offset, formatted_time, color)
                offset += 12
                stdscr.addstr(current_line, offset, description, color)

                current_line += 1
                alternate = not alternate

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
