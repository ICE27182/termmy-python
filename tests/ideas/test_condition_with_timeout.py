from threading import Thread, RLock, Condition
from time import sleep

def worker1(lock: RLock, condition: Condition):
    print("Worker 1 started.")
    with lock:
        print("Worker 1 acqures")
        print("Worker 1 waits")
        condition.wait(timeout=1)
        print("Worker 1 stops waiting and acquires.")
        print("Worker 1 sleeps.")
        sleep(3)
        print("Worker 1 wakes up. The END")

def worker2(lock, condition):
    print("Worker 2 started.")
    print("Worker 2 starts the initial sleep.")
    sleep(0.5)
    print("Worker 2 woke up from the initial sleep.")
    with lock:
        print("Worker 2 acquireds")
        print("Worker 2 sleeps")
        sleep(2)
        print("Worker 2 woke up again.")
        print("Worker2 releases.")


if __name__ == "__main__":
    print("""
        |-----------|-----------|-----------|-----------|-----------|-----------|-----------|------------|------------|------------|------------|------------|
        start      0.5          1          1.5          2          2.5          3          3.5           4           4.5           5           5.5           6
        Worker 1 started.
         Worker 1 acqures
          Worker 1 waits
           Worker 2 started.
            Worker 2 starts the initial sleep.
                    Worker 2 woke up from the initial sleep.
                     Worker 2 acquireds
                      worker 2 sleeps
                                                                    Worker 2 woke up again.
                                                                     Worker2 is about to releases.
                                                                      Worker 1 stops waiting and acquires.
                                                                       Worker 1 sleeps.
                                                                                                                                                Worker 1 wakes up again. The END
    """)
    lock = RLock()
    condition = Condition(lock)
    t1 = Thread(target=worker1, args=(lock, condition))
    t2 = Thread(target=worker2, args=(lock, condition))
    t1.start()
    t2.start()
    t1.join()
    t2.join
