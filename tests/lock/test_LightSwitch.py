from copy import copy
from threading import Lock, Thread
from time import sleep, time

from lox import LightSwitch

SLEEP_TIME = 0.01
N_WORKERS = 5

common_lock = None
counting_lock = None
resp_lock = None
resource = None


def common_setup():
    global common_lock, counting_lock, resp_lock

    common_lock = Lock()
    counting_lock = LightSwitch(common_lock)
    resp_lock = Lock()


def test_LightSwitch_1():
    global common_lock, counting_lock, resp_lock, resource
    common_setup()

    with counting_lock:
        acquired_lock = common_lock.acquire(timeout=0)
        assert acquired_lock is False
    acquired_lock = common_lock.acquire(timeout=0)
    assert acquired_lock is True
    common_lock.release()


def test_LightSwitch_len():
    global common_lock, counting_lock, resp_lock, resource
    common_setup()
    assert 0 == len(counting_lock)
    counting_lock.acquire()
    assert 1 == len(counting_lock)
    counting_lock.acquire()
    assert 2 == len(counting_lock)
    counting_lock.release()
    assert 1 == len(counting_lock)
    counting_lock.release()
    assert 0 == len(counting_lock)


def test_LightSwitch_timeout():
    lock = Lock()
    ls = LightSwitch(lock)
    lock.acquire()
    assert ls.acquire(timeout=SLEEP_TIME) is False
    assert ls.acquire(timeout=0) is False


def test_bathroom_example():
    sol = [
        "p_0_enter",
        "p_1_enter",
        "p_0_exit",
        "p_2_enter",
        "p_1_exit",
        "p_3_enter",
        "p_2_exit",
        "p_4_enter",
        "p_3_exit",
        "p_4_exit",
        "j_enter",
        "j_exit",
    ]

    res = bathroom_example()

    for r, s in zip(res, sol):
        assert r == s


def bathroom_example():
    """Bathroom analogy for light switch.

    Scenario:
        A janitor needs to clean a restroom, but is not allowed to enter until
        all people are out of the restroom. How do we implement this?
    """
    restroom_occupied = Lock()
    restroom = LightSwitch(restroom_occupied)
    res = []
    n_people = 5
    sleep_time = 0.2

    def janitor():
        with restroom_occupied:  # block until the restroom is no longer occupied
            res.append("j_enter")
            print("(%0.3f s) Janitor  entered the restroom" % (time() - t_start,))
            sleep(sleep_time)  # clean the restroom
            res.append("j_exit")
            print("(%0.3f s) Janitor  exited  the restroom" % (time() - t_start,))

    def people(id):
        if id == 0:  # Get the starting time of execution for display purposes
            global t_start
            t_start = time()
        with restroom:  # block if a janitor is in the restroom
            res.append("p_%d_enter" % (id,))
            print(
                "(%0.3f s) Person %d entered the restroom"
                % (
                    time() - t_start,
                    id,
                )
            )
            sleep(sleep_time)  # use the restroom
            res.append("p_%d_exit" % (id,))
            print(
                "(%0.3f s) Person %d exited  the restroom"
                % (
                    time() - t_start,
                    id,
                )
            )

    people_threads = [Thread(target=people, args=(i,)) for i in range(n_people)]
    janitor_thread = Thread(target=janitor)

    for i, person in enumerate(people_threads):
        person.start()  # Person i will now attempt to enter the restroom
        sleep(sleep_time * 0.6)  # wait for 60% the time a person spends in the restroom
        if i == 0:  # While the first person is in the restroom...
            janitor_thread.start()  # the janitor would like to enter. HOWEVER...
            print("(%0.3f s) Janitor Dispatched" % (time() - t_start))
    # Wait for all threads to finish
    for t in people_threads:
        t.join()
    janitor_thread.join()

    # The results will look like:
    """
    Running Restroom Demo
    (0.000 s) Person 0 entered the restroom
    (0.061 s) Person 1 entered the restroom
    (0.100 s) Person 0 exited  the restroom
    (0.122 s) Person 2 entered the restroom
    (0.162 s) Person 1 exited  the restroom
    (0.182 s) Person 3 entered the restroom
    (0.222 s) Person 2 exited  the restroom
    (0.243 s) Person 4 entered the restroom
    (0.282 s) Person 3 exited  the restroom
    (0.343 s) Person 4 exited  the restroom
    (0.343 s) Janitor  entered the restroom
    (0.443 s) Janitor  exited  the restroom
    """
    # Note that multiple people can be in the restroom.
    # If people kept using the restroom, the Janitor would never be able
    # to enter (technically known as thread starvation).
    # If this is undesired for your application, look at RWLock

    return res


if __name__ == "__main__":
    print("Running Restroom Demo")
    bathroom_example()
