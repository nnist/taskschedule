#!/bin/python3

import os
import subprocess
import time
import sys
import json


BRIGHTNESS_LOW = 0.3
BRIGHTNESS_HIGH = 0.52
GAMMA_LOW = "1.0:1.0:1.0"
GAMMA_HIGH = "1.0:1.0:1.0"
SLEEP_TIME = 0.2

home = os.path.expanduser("~")

data = ''.join(sys.stdin.readlines())
json_data = json.loads(data)

summary = "Scheduled task: {}".format(json_data['id'])
body = "{}".format(json_data['description'])

subprocess.run(["notify-send", "--urgency", "critical", summary, body])
subprocess.run(["aplay", home + "/.taskschedule/hooks/drip.wav"])
