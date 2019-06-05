import curses
import time

from taskschedule.schedule import Schedule


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

        # pylint: disable=invalid-name
        self.COLOR_DEFAULT = curses.color_pair(1)
        self.COLOR_DEFAULT_ALTERNATE = curses.color_pair(3)
        self.COLOR_HEADER = curses.color_pair(4) | curses.A_UNDERLINE
        self.COLOR_HOUR = curses.color_pair(2)
        self.COLOR_HOUR_CURRENT = curses.color_pair(5)
        self.COLOR_ACTIVE = curses.color_pair(8)
        self.COLOR_SHOULD_BE_ACTIVE = curses.color_pair(10)
        self.COLOR_OVERDUE = curses.color_pair(11)
        self.COLOR_COMPLETED = curses.color_pair(7)
        self.COLOR_COMPLETED_ALTERNATE = curses.color_pair(6)
        self.COLOR_GLYPH = curses.color_pair(9)

    def get_task_color(self, task, alternate):
        """Return the color for the given task."""
        color = None

        if task.active:
            color = self.COLOR_ACTIVE
        elif task.should_be_active:
            color = self.COLOR_SHOULD_BE_ACTIVE
        elif task.overdue and not task.completed:
            color = self.COLOR_OVERDUE
        else:
            if alternate:
                if task.completed:
                    color = self.COLOR_COMPLETED_ALTERNATE
                else:
                    color = self.COLOR_DEFAULT_ALTERNATE
            else:
                if task.completed:
                    color = self.COLOR_COMPLETED
                else:
                    color = self.COLOR_DEFAULT

        return color

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

        self.buffer.append((0, offsets[1], headers[2], self.COLOR_HEADER))
        self.buffer.append((0, offsets[2], headers[3], self.COLOR_HEADER))
        self.buffer.append((0, offsets[3], headers[4], self.COLOR_HEADER))

        if not self.hide_projects:
            self.buffer.append((0, offsets[4], headers[5], self.COLOR_HEADER))

        # Draw schedule
        alternate = True
        current_line = 1

        if self.hide_empty:
            first_task = schedule.tasks[0].start
            first_hour = first_task.hour
            last_task = schedule.tasks[-1].start
            last_hour = last_task.hour
        else:
            first_hour = 0
            last_hour = 23

        for i in range(first_hour, last_hour + 1):
            tasks = as_dict[i]
            if not tasks:
                # Add empty line
                if alternate:
                    color = self.COLOR_DEFAULT_ALTERNATE
                else:
                    color = self.COLOR_DEFAULT

                # Fill line to screen length
                self.buffer.append((current_line, 5, ' ' * (max_x - 5), color))

                # Draw hour, highlight current hour
                current_hour = time.localtime().tm_hour
                if i == current_hour:
                    self.buffer.append((current_line, 0, str(i),
                                        self.COLOR_HOUR_CURRENT))
                else:
                    self.buffer.append((current_line, 0, str(i),
                                        self.COLOR_HOUR))

                current_line += 1
                alternate = not alternate

            for ii, task in enumerate(tasks):
                color = self.get_task_color(task, alternate)

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
                                            self.COLOR_HOUR_CURRENT))
                    else:
                        self.buffer.append((current_line, 0, hour,
                                            self.COLOR_HOUR))

                # Fill line to screen length
                self.buffer.append((current_line, 5, ' ' * (max_x - 5),
                                    color))

                # Draw task details
                self.buffer.append((current_line, 3, task.glyph,
                                    self.COLOR_GLYPH))
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
