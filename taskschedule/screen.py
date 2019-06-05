import time
import curses
import datetime

from isodate import parse_duration

from taskschedule.schedule import Schedule
from taskschedule.scheduled_task import ScheduledTask


class Screen():
    def __init__(self, refresh_rate=1, hide_empty=True, scheduled_before='tomorrow',
                 scheduled_after='today',
                 completed=True, hide_projects=False):
        self.stdscr = curses.initscr()
        self.refresh_rate = refresh_rate
        self.completed = completed
        self.scheduled_before = scheduled_before
        self.scheduled_after = scheduled_after
        self.hide_projects = hide_projects
        self.hide_empty = hide_empty
        self.buffer = []
        self.prev_buffer = []
        self.init_colors()

    def close(self):
        curses.endwin()

    def init_colors(self):
        """Initialize the colors."""
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
        curses.init_pair(10, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Active task
        curses.init_pair(11, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Overdue task

    def draw(self):
        """Draw the current buffer."""
        if self.prev_buffer != self.buffer:
            for line, offset, string, color in self.buffer:
                max_y, max_x = self.stdscr.getmaxyx()
                if line < max_y - 1:
                    self.stdscr.addstr(line, offset, string, color)
                    self.stdscr.refresh()
                else:
                    break

    def draw_buffer(self):
        max_y, max_x = self.stdscr.getmaxyx()
        self.prev_buffer = self.buffer
        self.buffer = []

        schedule = Schedule()

        schedule.load_tasks(scheduled_before=self.scheduled_before,
                            scheduled_after=self.scheduled_after,
                            completed=self.completed)

        as_dict = schedule.as_dict()

        # Determine offsets
        offsets = schedule.get_column_offsets()

        # Draw headers
        headers = ['', '', 'ID', 'Time', 'Project', 'Description']

        color = curses.color_pair(4) | curses.A_UNDERLINE
        self.buffer.append((0, offsets[1], headers[2], color))
        self.buffer.append((0, offsets[2], headers[3], color))
        self.buffer.append((0, offsets[3], headers[4], color))

        if not self.hide_projects:
            self.buffer.append((0, offsets[4], headers[5], color))

        # Draw schedule
        past_first_task = False
        alternate = True
        current_line = 1
        for i in range(24):
            tasks = as_dict[i]
            if not tasks:
                # Add empty line if between tasks or option is enabled
                if past_first_task or not self.hide_empty:
                    if alternate:
                        color = curses.color_pair(1)
                    else:
                        color = curses.color_pair(3)

                    # Fill line to screen length
                    self.buffer.append((current_line, 5,
                                        ' ' * (max_x - 5), color))

                    # Draw hour, highlight current hour
                    current_hour = time.localtime().tm_hour
                    if i == current_hour:
                        self.buffer.append((current_line, 0, str(i),
                                            curses.color_pair(5)))
                    else:
                        self.buffer.append((current_line, 0, str(i),
                                            curses.color_pair(2)))

                    current_line += 1
                    alternate = not alternate

            for ii, task in enumerate(tasks):
                is_current_task = task.should_be_active

                past_first_task = True
                if task.active:
                    color = curses.color_pair(8)
                elif is_current_task:
                    color = curses.color_pair(10)
                elif task.overdue and not task.completed:
                    color = curses.color_pair(11)
                else:
                    if alternate:
                        if task.completed:
                            color = curses.color_pair(7)
                        else:
                            color = curses.color_pair(1)
                    else:
                        if task.completed:
                            color = curses.color_pair(6)
                        else:
                            color = curses.color_pair(3)

                # Only draw hour once for multiple tasks
                if ii == 0:
                    hour = str(i)
                else:
                    hour = ''

                if task.end is None:
                    formatted_time = '{}'.format(task.start_time)
                else:
                    end_time = '{}'.format(task.end.strftime('%H:%M'))
                    formatted_time = '{}-{}'.format(task.start_time,
                                                    end_time)

                # Draw hour, highlight current hour
                current_hour = time.localtime().tm_hour
                if hour != '':
                    if int(hour) == current_hour:
                        self.buffer.append((current_line, 0, hour,
                                            curses.color_pair(5)))
                    else:
                        self.buffer.append((current_line, 0, hour,
                                            curses.color_pair(2)))

                # Fill line to screen length
                self.buffer.append((current_line, 5, ' ' * (max_x - 5),
                                    color))

                # Draw task details
                self.buffer.append((current_line, 3, task.glyph,
                                    curses.color_pair(9)))
                if task.task_id != 0:
                    self.buffer.append((current_line, 5, str(task.task_id),
                                        color))

                self.buffer.append((current_line, offsets[2],
                                    formatted_time, color))

                # Optionally draw project column
                offset = 0
                if not self.hide_projects:
                    if task.project is None:
                        project = ''
                    else:
                        project = task.project

                    self.buffer.append((current_line, offsets[3], project,
                                        color))
                    offset = offsets[4]
                else:
                    offset = offsets[3]

                # Draw description column
                description = task.description[0:max_x - offset]
                self.buffer.append((current_line, offset,
                                    description, color))

                current_line += 1
                alternate = not alternate
