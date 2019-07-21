import subprocess
import os

def run_hooks():
    # TODO Assign types to hooks, i.e. 'on-modify', 'on-new-active'

    home = os.path.expanduser("~")

    hooks_directory = home + '/.taskschedule/hooks'
    onlyfiles = [f for f in os.listdir(hooks_directory) if os.path.isfile(os.path.join(hooks_directory, f))]

    for filename in onlyfiles:
        subprocess.Popen([home + '/.taskschedule/hooks/' + filename], shell=True)
