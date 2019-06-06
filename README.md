# Taskschedule
This is a time schedule report for [taskwarrior](https://taskwarrior.org/).

Features:
- Schedule is updated real-time
- Schedule can be printed like a regular taskwarrior report
- Active tasks are highlighted
- Completed tasks can be shown or hidden

## Requirements
- taskwarrior
- in `.taskrc`:
    ```
    # User Defined Attributes
    uda.estimate.type=duration
    uda.estimate.label=Est
    ```

## Usage
1. Start taskschedule
```
$ taskschedule
```
2. In a new terminal, create a scheduled task
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
4. Start the task in taskwarrior
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
6. Mark task as done
```
$ task 62 done
```
```
     ID Time  Description
16
17 ○    17:00 Buy cat food        <-- barely visible
18
```
