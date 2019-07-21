import subprocess
import os
import json


def run_hooks(hook_type, data={'id': -1, 'description': 'none'}):
    """Run hook scripts in the hooks directory.

       :param hook_type: the hook type to run.
                         valid values: 'on-progress'
       :param data: the JSON data to pass as a string to stdin."""

    home = os.path.expanduser("~")

    hooks_directory = home + '/.taskschedule/hooks'
    onlyfiles = [f for f in os.listdir(hooks_directory) if os.path.isfile(os.path.join(hooks_directory, f))]

    for filename in onlyfiles:
        if hook_type == 'on-progress' and filename.startswith('on-progress-'):
            input_data = json.dumps(data, ensure_ascii=False).encode('utf8')
            result = subprocess.run(
                [home + '/.taskschedule/hooks/' + filename],
                shell=True,
                stdout=subprocess.PIPE,
                input=input_data
            )
            #print(result.stdout.decode('utf-8'))
