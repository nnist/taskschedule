"""Command line interface of taskschedule"""

import argparse
import os
import sys
import time
from curses import KEY_DOWN, KEY_RESIZE, KEY_UP
from curses import error as curses_error
from curses import napms

from tasklib import TaskWarrior

from taskschedule.notifier import Notifier
from taskschedule.schedule import (
    Schedule,
    TaskDirDoesNotExistError,
    TaskrcDoesNotExistError,
    UDADoesNotExistError,
)
from taskschedule.screen import Screen
from taskschedule.taskwarrior import PatchedTaskWarrior
from taskschedule.utils import calculate_datetime


def main(argv):
    """Display a schedule report for taskwarrior."""
    home = os.path.expanduser("~")

    parser = argparse.ArgumentParser(
        description="""Display a schedule report for taskwarrior."""
    )
    parser.add_argument(
        "-r", "--refresh", help="refresh every n seconds", type=int, default=1
    )
    parser.add_argument(
        "--from",
        help="scheduled from date: ex. 'today', 'tomorrow'",
        type=str,
        dest="after",
        default="today-1s",
    )
    parser.add_argument(
        "--to",
        "--until",
        help="scheduled until date: ex. 'today', 'tomorrow'",
        type=str,
        dest="before",
        default="tomorrow-1s",
    )
    parser.add_argument(
        "-d",
        "--data-location",
        help="""data location (e.g. ~/.task)""",
        type=str,
        dest="data_location",
        default=f"{home}/.task",
    )
    parser.add_argument(
        "-t",
        "--taskrc-location",
        help="""taskrc location (e.g. ~/.taskrc)""",
        type=str,
        dest="taskrc_location",
        default=f"{home}/.taskrc",
    )
    parser.add_argument(
        "-a",
        "--all",
        help="show all hours, even if empty",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-c",
        "--completed",
        help="hide completed tasks",
        action="store_false",
        default=True,
    )
    parser.add_argument(
        "-p",
        "--project",
        help="hide project column",
        action="store_true",
        default=False,
    )
    args = parser.parse_args(argv)

    if args.before and not args.after or not args.before and args.after:
        print("Error: Either both --until and --from or neither options must be used.")
        sys.exit(1)

    if not args.before:
        args.before = "tomorrow"
    if not args.after:
        args.after = "yesterday"

    taskschedule_dir = home + "/.taskschedule"
    hooks_directory = home + "/.taskschedule/hooks"

    if not os.path.isdir(taskschedule_dir):
        os.mkdir(taskschedule_dir)
    if not os.path.isdir(hooks_directory):
        os.mkdir(hooks_directory)

    # Setup the backend
    taskwarrior = TaskWarrior(
        data_location=args.data_location,
        create=False,
        taskrc_location=args.taskrc_location,
    )

    # Disable _forcecolor because it breaks tw config output
    taskwarrior.overrides.update({"_forcecolor": "off"})

    if os.path.isdir(args.data_location) is False:
        raise TaskDirDoesNotExistError(".task directory not found")
    if os.path.isfile(args.taskrc_location) is False:
        raise TaskrcDoesNotExistError(".taskrc not found")
    if taskwarrior.config.get("uda.estimate.type") is None:
        raise UDADoesNotExistError(("uda.estimate.type does not exist " "in .taskrc"))
    if taskwarrior.config.get("uda.estimate.label") is None:
        raise UDADoesNotExistError(("uda.estimate.label does not exist " "in .taskrc"))

    task_command_args = ["task", "status.not:deleted"]

    # Parse schedule date range
    scheduled_after = calculate_datetime(args.after)
    scheduled_before = calculate_datetime(args.before)

    task_command_args.append(f"scheduled.after:{scheduled_after}")
    task_command_args.append(f"scheduled.before:{scheduled_before}")

    if not args.completed:
        task_command_args.append(f"status.not:{args.completed}")

    backend = PatchedTaskWarrior(
        data_location=args.data_location,
        create=False,
        taskrc_location=args.taskrc_location,
        task_command=" ".join(task_command_args),
    )

    schedule = Schedule(
        backend, scheduled_after=scheduled_after, scheduled_before=scheduled_before
    )
    notifier = Notifier(backend)

    try:
        screen = Screen(
            schedule,
            scheduled_after=scheduled_after,
            scheduled_before=scheduled_before,
            hide_empty=not args.all,
            hide_projects=args.project,
        )

        # TODO Refresh on any file change in dir instead of every second
        last_refresh_time = 0.0
        while True:
            key = screen.stdscr.getch()
            if key == 113:  # q
                break
            elif key == 65 or key == 107:  # Up / k
                screen.scroll(-1)
                last_refresh_time = time.time()
            elif key == 66 or key == 106:  # Down / j
                screen.scroll(1)
                last_refresh_time = time.time()
            elif key == 54:  # Page down
                max_y, max_x = screen.get_maxyx()
                screen.scroll(max_y - 4)
                last_refresh_time = time.time()
            elif key == 53:  # Page up
                max_y, max_x = screen.get_maxyx()
                screen.scroll(-(max_y - 4))
                last_refresh_time = time.time()
            elif key == KEY_RESIZE or time.time() > last_refresh_time + args.refresh:
                notifier.send_notifications()
                last_refresh_time = time.time()
                schedule.clear_cache()
                screen.refresh_buffer()
                screen.draw()
                napms(50)

            napms(1)

            if args.refresh < 0:
                break
    except TaskDirDoesNotExistError as err:
        print("Error: {}".format(err))
        sys.exit(1)
    except TaskrcDoesNotExistError as err:
        print("Error: {}".format(err))
        sys.exit(1)
    except KeyboardInterrupt:
        screen.close()
    except ValueError as err:
        screen.close()
        print("Error: {}".format(err))
        sys.exit(1)
    except UDADoesNotExistError as err:
        screen.close()
        print("Error: {}".format(err))
        sys.exit(1)
    else:
        try:
            screen.close()
        except curses_error as err:
            print(err.with_traceback)
