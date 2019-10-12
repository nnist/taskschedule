import os
import shutil

import pytest

from taskschedule.taskwarrior import PatchedTaskWarrior


@pytest.fixture(scope="module")
def tw():
    """Create a PatchedTaskWarrior instance with a temporary .taskrc and data
       location. Remove the temporary data after testing is finished."""

    taskrc_path = "tests/test-data/.taskrc"
    task_dir_path = "tests/test-data/.task"

    # Create a sample .taskrc
    with open(taskrc_path, "w+") as file:
        file.write("# User Defined Attributes\n")
        file.write("uda.estimate.type=duration\n")
        file.write("uda.estimate.label=Est\n")
        file.write("# User Defined Attributes\n")
        file.write("uda.tb_estimate.type=numeric\n")
        file.write("uda.tb_estimate.label=Est\n")
        file.write("uda.tb_real.type=numeric\n")
        file.write("uda.tb_real.label=Real\n")

    # Create a sample empty .task directory
    os.makedirs(task_dir_path)

    tw = PatchedTaskWarrior(
        data_location=task_dir_path, create=True, taskrc_location=taskrc_path
    )
    tw.overrides.update({"uda.estimate.type": "duration"})
    tw.overrides.update({"uda.estimate.label": "Est"})

    yield tw

    try:
        os.remove(taskrc_path)
    except FileNotFoundError:
        pass

    try:
        shutil.rmtree(task_dir_path)
    except FileNotFoundError:
        pass
