import time


class Limiter:

    def __init__(self, times, seconds=1, autosleep=True):
        self.times = times
        self.seconds = seconds
        self.autosleep = autosleep

        self._calls = 0

    def limit(self):
        current_time = time.time()
        if self._calls == 0:
            self._start = current_time
            self._end = current_time + self.seconds

        self._calls += 1

        if current_time >= self._end:
            self._calls = 0
        elif self._calls >= self.times:
            self._calls = 0
            sleep = self._end - current_time
            if self.autosleep:
                time.sleep(sleep)
            return sleep

    def clone(self):
        return Limiter(times=self.times, seconds=self.seconds)


if __name__ == '__main__':
    limiter = Limiter(4)

    for i in range(10):
        print('->', i)
        sleep = limiter.limit()
        print('Slept for', sleep, 'seconds')
