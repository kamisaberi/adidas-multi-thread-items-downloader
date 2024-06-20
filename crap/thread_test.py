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
        prb = random.random()
        if prb >= 0.5:
            print(k, "WRITE FILE")
            tt = TestThread(thread_id=k, write_file=True)
        else:
            print(k, "NOTHING")
            tt = TestThread(thread_id=k, write_file=False)
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
            print("locked")
            time.sleep(0.5)
            continue
        if self.write_file:
            if not lock.locked():
                lock.acquire()
                print(lock.locked())
                print("locked")
                print("WRITING INTO FILE STARTED")
                time.sleep(5)
                print("WRITING INTO FILE FINISHED")
                lock.release()
                print(lock.locked())
                print("locked")
        else:
            print("REGULAR THREAD")


if __name__ == "__main__":
    main()
