import threading
import time
import sys

class Timer:
    def __init__(self):
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run_timer)
        self._start_time = None

    def start(self):
        self._start_time = time.time()
        self._thread.start()

    def _run_timer(self):
        while not self._stop_event.is_set():
            elapsed_time = time.time() - self._start_time
            sys.stdout.write(f"\rRunning: {elapsed_time:.0f}s...")
            time.sleep(1)

    def end(self):
        self._stop_event.set()
        self._thread.join()
        elapsed_time = time.time() - self._start_time
        print(f"\nTotal Running Time: {elapsed_time:.0f}s\n")
