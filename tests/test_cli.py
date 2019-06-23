# pylint: disable=missing-docstring,no-self-use

import subprocess
import unittest
import os
import shutil
import time
import sys

from .context import taskschedule


class Timeout(Exception):
    pass


def run(command, timeout=10):
    proc = subprocess.Popen(command, bufsize=0)
    poll_seconds = .250
    deadline = time.time()+timeout
    while time.time() < deadline and proc.poll() is None:
        time.sleep(poll_seconds)

    if proc.poll() is None:
        if float(sys.version[:3]) >= 2.6:
            proc.terminate()
            proc.wait()

        raise Timeout()

    stdout, stderr = proc.communicate()
    return stdout, stderr, proc.returncode


class CLITest(unittest.TestCase):
    def setUp(self):
        self.taskrc_path = 'tests/test_data/.taskrc'
        self.task_dir_path = 'tests/test_data/.task'
        self.assertEqual(os.path.isfile(self.taskrc_path), False)
        self.assertEqual(os.path.isdir(self.task_dir_path), False)

        # Create a sample .taskrc
        with open(self.taskrc_path, 'w+') as file:
            file.write('# User Defined Attributes\n')
            file.write('uda.estimate.type=duration\n')
            file.write('uda.estimate.label=Est\n')

        # Create a sample empty .task directory
        os.makedirs(self.task_dir_path)

        self.assertEqual(os.path.isfile(self.taskrc_path), True)
        self.assertEqual(os.path.isdir(self.task_dir_path), True)

    def tearDown(self):
        os.remove(self.taskrc_path)
        shutil.rmtree(self.task_dir_path)

    def test_cli_valid_date_does_not_error(self):
        # Ensure it times out, because that means it atleast
        # entered the main loop
        try:
            run(['python3', '__main__.py', '--from', 'today', '--until',
                 'tomorrow'], timeout=2)
        except Timeout:
            pass

        try:
            run(['python3', '__main__.py', '--scheduled', 'tomorrow'],
                timeout=2)
        except Timeout:
            pass

    def test_cli_invalid_date_prints_error(self):
        try:
            process = subprocess.run(
                ['python3 __main__.py --from asdfafk --until tomorrow'],
                shell=True,
                timeout=10,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, check=True)
            output = process.stdout.split(b'\n')
            self.assertEqual(
                output[0], b"Error: time data 'asdfafk' does not match format '%Y-%m-%dT%H:%M:%S'")
        except subprocess.CalledProcessError:
            pass
        try:
            process = subprocess.run(
                ['python3 __main__.py --scheduled asdfafk'],
                shell=True,
                timeout=10,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, check=True)
            output = process.stdout.split(b'\n')
            self.assertEqual(
                output[0], b"Error: time data 'asdfafk' does not match format '%Y-%m-%dT%H:%M:%S'")
        except subprocess.CalledProcessError:
            pass

    def test_cli_no_args_does_not_error(self):
        # Ensure it times out, because that means it atleast
        # entered the main loop
        try:
            run(["python3", "__main__.py"], timeout=2)
        except Timeout:
            pass

    def test_cli_help_returns_help_message(self):
        process = subprocess.run(['python3 __main__.py -h'],
                                 shell=True,
                                 timeout=10,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, check=True)
        output = process.stdout.split(b'\n')
        assert output[0].startswith(b'usage:')


if __name__ == '__main__':
    unittest.main()
