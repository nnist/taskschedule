# pylint: disable=missing-docstring,no-self-use

import subprocess
import unittest
import os
import shutil

from .context import taskschedule


class CLITest(unittest.TestCase):
    def setUp(self):
        # Make sure ~/.taskrc and ~/.task/ do not exist to prevent damage
        home = os.path.expanduser("~")
        self.assertEqual(os.path.isfile(home + '/.taskrc'), False)
        self.assertEqual(os.path.isdir(home + '/.task'), False)

        # Create a sample ~/.taskrc
        with open(home + '/.taskrc', 'w+') as file:
            file.write('# User Defined Attributes\n')
            file.write('uda.estimate.type=duration\n')
            file.write('uda.estimate.label=Est\n')

        with open('tests/test_data/.task/.taskrc', 'w') as file:
            file.write('# User Defined Attributes\n')
            file.write('uda.estimate.type=duration\n')
            file.write('uda.estimate.label=Est\n')

        os.makedirs(home + '/.task')
        self.assertEqual(os.path.isfile(home + '/.taskrc'), True)
        self.assertEqual(os.path.isdir(home + '/.task'), True)

    def tearDown(self):
        home = os.path.expanduser("~")
        try:
            os.remove(home + '/.taskrc')
        except FileNotFoundError:
            pass

        try:
            shutil.rmtree(home + '/.task')
        except FileNotFoundError:
            pass

    def test_cli_valid_date_does_not_error(self):
        # Ensure it times out, because that means it atleast
        # entered the main loop
        try:
            subprocess.run(
                ['python3 __main__.py -t tests/test_data/.task/.taskrc -d tests/test_data/.task/ --from today --until tomorrow'],
                shell=True,
                timeout=1,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, check=True)
        except subprocess.TimeoutExpired:
            pass
        try:
            subprocess.run(
                ['python3 __main__.py -t tests/test_data/.task/.taskrc -d tests/test_data/.task/ --scheduled tomorrow'],
                shell=True,
                timeout=1,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, check=True)
        except subprocess.TimeoutExpired:
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
            self.assertEqual(output[0], b"Error: time data 'asdfafk' does not match format '%Y-%m-%dT%H:%M:%S'")
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
            self.assertEqual(output[0], b"Error: time data 'asdfafk' does not match format '%Y-%m-%dT%H:%M:%S'")
        except subprocess.CalledProcessError:
            pass

    def test_cli_no_args_does_not_error(self):
        # Ensure it times out, because that means it atleast
        # entered the main loop
        try:
            subprocess.run(
                ['python3 __main__.py'],
                shell=True,
                timeout=1,
                check=True)
        except subprocess.CalledProcessError as err:
            print(err)
            print(err.output)
        except subprocess.TimeoutExpired:
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
