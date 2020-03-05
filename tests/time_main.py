from subprocess import call
import time


class TimeMain:

    def time(self):
        time_before = time.perf_counter()
        call(['python', '../generator/main.py',
              '../source_plays/a_dolls_house.htm'])
        time_after = time.perf_counter()

        diff_training = time_after - time_before
        print('Time to produce play:', diff_training, 'seconds')


if __name__ == '__main__':
    timer = TimeMain()
    timer.time()
