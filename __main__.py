#!/usr/bin/env python3

import sys
import os

import taskschedule.main

if __name__ == "__main__":
    try:
        taskschedule.main.main(sys.argv[1:])
    except KeyboardInterrupt:
        print('Interrupted by user.')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0) # pylint: disable=protected-access
