import subprocess
import os


def run_hooks(hook_type):
    """Run hook scripts in the hooks directory.

       :param hook_type: the hook type to run.
                         valid values: 'on-progress'"""

    home = os.path.expanduser("~")

    hooks_directory = home + '/.taskschedule/hooks'
    onlyfiles = [f for f in os.listdir(hooks_directory) if os.path.isfile(os.path.join(hooks_directory, f))]

    for filename in onlyfiles:
        if hook_type == 'on-progress' and filename.startswith('on-progress-'):
            subprocess.Popen([home + '/.taskschedule/hooks/' + filename], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
