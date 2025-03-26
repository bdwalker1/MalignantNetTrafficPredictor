import time


class SimpleTimer:

    def __init__(self):
        self.__running = False
        self.__start = -1
        self.__end = -1
        self.__laptimes = []

    @staticmethod
    def __time_diff(s, e):
        return abs(e - s)

    def reset(self):
        self.__running = False
        self.__start = -1
        self.__end = -1
        self.__laptimes = []

    def start(self):
        if self.__running:
            raise Exception("Timer already running. Must stop before starting.")
        else:
            self.reset()
            self.__start = time.time()
            self.__running = True

    def stop(self, is_last_lap=True):
        if not self.__running:
            raise Exception("Timer not running. Must start before stopping.")
        else:
            if is_last_lap:
                _ = self.laptime()
            self.__end = time.time()
            self.__running = False
            return self.__time_diff(self.__start, self.__end)

    def elapsed(self):
        if self.__running:
            return self.__time_diff(self.__start, time.time())
        else:
            return self.__time_diff(self.__start, self.__end)

    def laptime(self):
        if not self.__running:
            raise Exception("Timer not running. Must start before getting lap times.")
        else:
            self.__laptimes.append(time.time())
            if len(self.__laptimes) == 1:
                elapsed_time = self.__time_diff(self.__start, self.__laptimes[0])
            else:
                elapsed_time = self.__time_diff(self.__laptimes[-2], self.__laptimes[-1])
            return elapsed_time

    def show_laptimes(self):
        laptimes = self.__laptimes
        lap_count = len(laptimes)
        if lap_count > 0:
            for n in range(0, lap_count):
                if n == 0:
                    span = self.__time_diff(self.__start, laptimes[n])
                else:
                    span = self.__time_diff(laptimes[n - 1], laptimes[n])
                print(f"Lap {n + 1}: {self.sts(span)}")
            if not self.__running:
                if self.__time_diff(laptimes[-1], self.__end) > .0001:
                    span = self.__time_diff(laptimes[-1], self.__end)
                    print(f"After Last Lap: {self.sts(span)}")

    @staticmethod
    def sts(seconds):  # Span to String

        # Extract days, hours, minutes, and seconds
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        output = ""
        if days > 0:
            output += f"{int(days)}d "
        if (days > 0) or (hours > 0):
            output += f"{int(hours)}h "
        if (days > 0) or (hours > 0) or (minutes > 0):
            output += f"{int(minutes)}m "
        output += f"{seconds:.3f}s"
        return output.strip()
