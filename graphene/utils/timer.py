import time

class CmdTimer:
    def __init__(self):
        self.running = False
        self.paused = False
        self.cur_start = None
        self.time_elapsed = 0

    def start(self):
        if self.paused:
            self.paused = False
        else:
            self.time_elapsed = 0
        self.cur_start = time.time()
        self.running = True

    def pause(self):
        if self.cur_start is None:
            return
        self.time_elapsed += time.time() - self.cur_start
        self.cur_start = None
        self.paused = True
        self.running = False
        self.cur_start = None

    def stop(self):
        self.paused = False
        self.running = False
        # If we weren't paused, then add what was left over
        if self.cur_start is not None:
            self.time_elapsed += time.time() - self.cur_start
