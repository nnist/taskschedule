from tasklib import TaskWarrior

class Schedule():
    def __init__(self, tw_data_dir='~/.task', tw_data_dir_create=False):
        self.tw_data_dir = tw_data_dir
        self.tw_data_dir_create = tw_data_dir_create

    def get_tasks(self):
        taskwarrior = TaskWarrior(self.tw_data_dir, self.tw_data_dir_create)
        self.tasks = taskwarrior.tasks.filter(scheduled='today',
                                              status='pending')
