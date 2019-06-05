"""Command line interface of taskschedule"""

import argparse
import time

from taskschedule.screen import Screen


def main(argv):
    """Display a schedule report for taskwarrior."""
    parser = argparse.ArgumentParser(
        description="""Display a schedule report for taskwarrior."""
    )
    parser.add_argument(
        '-r', '--refresh', help="refresh every n seconds", type=int, default=1
    )
    parser.add_argument(
        '--after', help="scheduled after date: ex. 'today', 'tomorrow'",
        type=str, default='today'
    )
    parser.add_argument(
        '--before', help="scheduled before date: ex. 'today', 'tomorrow'",
        type=str, default='tomorrow'
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

    screen = Screen(hide_empty=hide_empty,
                    scheduled_before=args.before,
                    scheduled_after=args.after,
                    completed=args.completed, hide_projects=args.project)

    try:
        while True:
            screen.refresh_buffer()
            screen.draw()
            time.sleep(args.refresh)
    except KeyboardInterrupt:
        pass
    finally:
        screen.close()
