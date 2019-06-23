# pylint: disable=missing-docstring,no-self-use

import unittest
import os
import shutil

from taskschedule.main import main


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

    def test_main(self):
        main(['-r', '-1'])


if __name__ == '__main__':
    unittest.main()
