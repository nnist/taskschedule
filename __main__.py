#!/usr/bin/env python3

import os
import sys

from taskschedule.main import Main

if __name__ == "__main__":
    try:
        main = Main(sys.argv[1:])
        main.main()
    except KeyboardInterrupt:
        print("Interrupted by user.")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)  # pylint: disable=protected-access
