import sys
import os
import time
import curses
import argparse

from taskschedule.schedule import Schedule

def draw(stdscr, refresh_rate=1, hide_empty=True):
    schedule = Schedule()
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, 8, 0)

    while True:
        max_y, max_x = stdscr.getmaxyx()

        stdscr.clear()

        schedule.get_tasks()
        rows = schedule.format_as_table(hide_empty=hide_empty).splitlines()
        header = rows[0]
        data = rows[1:]

        for i, char in enumerate(header):
            if char == ' ':
                color = curses.color_pair(1)
            else:
                color = curses.color_pair(1) | curses.A_UNDERLINE
            stdscr.addstr(0, i, char, color)

        for i, row in enumerate(data):
            stdscr.addstr(i+1, 0, row[:2], curses.color_pair(2))

            details = row[2:]
            if len(details) > max_x:
                details = details[0:max_x - 5] + '...'

            stdscr.addstr(i+1, 2, details, curses.color_pair(1))

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
        '-a', '--all', help="show all hours, even if empty",
        action='store_true', default=False
    )
    args = parser.parse_args(argv)

    hide_empty = not args.all
    curses.wrapper(draw, args.refresh, hide_empty)
