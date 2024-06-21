import threading
import random
import time

lock = threading.Lock()


def main():
    threads: list[TestThread] = list()
    k = 1
    while True:
        time.sleep(1)
        if threading.active_count() > 10:
            continue
        tt = TestThread(thread_id=k, write_file=True, daemon=True)
        tt.start()
        tt.join(0.1)
        threads.append(tt)
        k += 1


class TestThread(threading.Thread):
    def __init__(self, thread_id: int, write_file: bool, group=None, target=None, name=None, args=(), kwargs=None, *,
                 daemon=None):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.thread_id = thread_id
        self.write_file = write_file

    def run(self):
        while lock.locked():
            time.sleep(0.5)
            continue
        lock.acquire()
        print(self.thread_id, "WRITING INTO FILE STARTED")
        time.sleep(5)
        print(self.thread_id, "WRITING INTO FILE FINISHED")
        lock.release()


if __name__ == "__main__":
    main()
