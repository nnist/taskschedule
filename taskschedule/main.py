import sys
import os
import time
import curses
import argparse

from taskschedule.schedule import Schedule

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
