"""Command line interface of taskschedule"""

import argparse
import time
import sys
import os

from curses import napms, KEY_RESIZE, KEY_DOWN, KEY_UP

from taskschedule.screen import Screen
from taskschedule.schedule import UDADoesNotExistError,\
                                  TaskrcDoesNotExistError,\
                                  TaskDirDoesNotExistError


def main(argv):
    """Display a schedule report for taskwarrior."""
    parser = argparse.ArgumentParser(
        description="""Display a schedule report for taskwarrior."""
    )
    parser.add_argument(
        '-r', '--refresh', help="refresh every n seconds", type=int, default=1
    )
    parser.add_argument(
        '--from', help="scheduled from date: ex. 'today', 'tomorrow'",
        type=str, dest='after'
    )
    parser.add_argument(
        '--to', '--until',
        help="scheduled until date: ex. 'today', 'tomorrow'",
        type=str, dest='before'
    )
    parser.add_argument(
        '-s', '--scheduled',
        help="""scheduled date: ex. 'today', 'tomorrow'
                (overrides --from and --until)""",
        type=str
    )
    parser.add_argument(
        '-d', '--data-location',
        help="""data location (e.g. ~/.task)""",
        type=str, dest='data_location'
    )
    parser.add_argument(
        '-t', '--taskrc-location',
        help="""taskrc location (e.g. ~/.taskrc)""",
        type=str, dest='taskrc_location'
    )
    parser.add_argument(
        '-a', '--all', help="show all hours, even if empty",
        action='store_true', default=False
    )
    parser.add_argument(
        '-c', '--completed', help="hide completed tasks",
        action='store_false', default=True
    )
    parser.add_argument(
        '-p', '--project', help="hide project column",
        action='store_true', default=False
    )
    args = parser.parse_args(argv)

    hide_empty = not args.all

    if args.scheduled:
        if args.before or args.after:
            print('Error: The --scheduled option can not be used together '
                  'with --until and/or --from.')
            sys.exit(1)
    else:
        if args.before and not args.after or not args.before and args.after:
            print('Error: Either both --until and --from or neither options '
                  'must be used.')
            sys.exit(1)

        if not args.before and not args.after:
            args.scheduled = 'today'
        elif not args.before:
            args.before = 'tomorrow'
        elif not args.after:
            args.after = 'yesterday'

    try:
        screen = Screen(tw_data_dir=args.data_location,
                        taskrc_location=args.taskrc_location,
                        hide_empty=hide_empty,
                        scheduled_before=args.before,
                        scheduled_after=args.after,
                        scheduled=args.scheduled,
                        completed=args.completed, hide_projects=args.project)
    except TaskDirDoesNotExistError as err:
        print('Error: {}'.format(err))
        sys.exit(1)
    except TaskrcDoesNotExistError as err:
        print('Error: {}'.format(err))
        sys.exit(1)

    last_refresh_time = 0
    try:
        while True:
            key = screen.stdscr.getch()
            if key == 113:
                break
            elif key == 65:
                screen.scroll(-1)
            elif key == 66:
                screen.scroll(1)
            elif (key == KEY_RESIZE or
                    time.time() > last_refresh_time + args.refresh):
                last_refresh_time = time.time()
                screen.refresh_buffer()
                screen.draw()
                napms(50)

            napms(1)
    except KeyboardInterrupt:
        pass
    except ValueError as err:
        screen.close()
        print('Error: {}'.format(err))
        sys.exit(1)
    except UDADoesNotExistError as err:
        screen.close()
        print('Error: {}'.format(err))
        sys.exit(1)
    finally:
        screen.close()
