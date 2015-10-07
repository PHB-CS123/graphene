from contextlib import contextmanager
import time

class CmdTimer:
    def __init__(self):
        self.running = False
        self.__paused = False
        self.cur_start = None
        self.time_elapsed = 0

    def start(self):
        if self.__paused:
            self.__paused = False
        else:
            self.time_elapsed = 0
        self.cur_start = time.time()
        self.running = True

    @contextmanager
    def paused(self):
        self.__pause()
        yield
        self.start()

    def __pause(self):
        if self.cur_start is None:
            return
        self.time_elapsed += time.time() - self.cur_start
        self.cur_start = None
        self.__paused = True
        self.running = False
        self.cur_start = None

    def stop(self):
        self.__paused = False
        self.running = False
        # If we weren't paused, then add what was left over
        if self.cur_start is not None:
            self.time_elapsed += time.time() - self.cur_start
