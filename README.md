[![Build status](https://travis-ci.org/nnist/taskschedule.svg?branch=master)](https://travis-ci.org/nnist/taskschedule) [![codecov](https://codecov.io/gh/nnist/taskschedule/branch/master/graph/badge.svg)](https://codecov.io/gh/nnist/taskschedule)  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Taskschedule
This is a time schedule report for [taskwarrior](https://taskwarrior.org/).

![screenshot](https://github.com/nnist/taskschedule/blob/master/img/screenshot.png "Screenshot")

## Features
- Hook support

## Getting started
### Prerequisites
- taskwarrior
- in `.taskrc`:
    ```
    # User Defined Attributes
    uda.estimate.type=duration
    uda.estimate.label=Est
    ```
### Installing
First, clone the repo:
```sh
$ git clone https://github.com/nnist/taskschedule.git
$ cd taskschedule
```
#### Method one
Install the program using setup.py:
```sh
$ python3 setup.py install
$ taskschedule
```
#### Method two
Instead of installing, you can also just run the program directly:
```sh
$ pip3 install --user -r requirements.txt
$ python3 __main__.py
```
## Usage
### Basic usage
1. Start taskschedule:
```
$ taskschedule
```
2. In a new terminal, create a scheduled task:
```
$ task add Buy cat food schedule:17:00
Created task 62.
```
3. The task will now be visible in taskschedule:
```
     ID Time  Description
16
17 ○ 62 17:00 Buy cat food
18
```
4. Start the task in taskwarrior:
```
$ task 62 start
```
5. The task is now displayed as active in taskschedule:
```
     ID Time  Description
16
17 ○ 62 17:00 Buy cat food        <-- highlighted
18
```
6. Mark the task as done:
```
$ task 62 done
```
```
     ID Time  Description
16
17 ○    17:00 Buy cat food        <-- barely visible
18
```
### Show tomorrow's tasks
```sh
$ taskschedule -s tomorrow
```
### Show last week's tasks
```sh
$ taskschedule --from today-1week --to tomorrow
```
### Hooks
Scripts in the hook directory (default: `~/.taskschedule/hooks/`) are
automatically run on certain triggers. For example, the `on-progress` hook
runs all scripts starting with `on-progress`, e.g. `on-progress-notify.py`.

This can be used to for things like notification pop-ups, alarm sounds,
push notifications, etc.

## Running the tests
First go to the repo root, then run the tests:
```sh
$ python3 -m unittest
```
## License
This project is licensed under the MIT License - see the `LICENSE` file for details.
