import threading
from lox import RWLock
from copy import copy
from time import sleep, time
from collections import deque

SLEEP_TIME = 0.01
N_WORKERS = 5

rw_lock = None
resource = None
resp = None

def common_setup():
    global rw_lock, resp
    rw_lock = RWLock()
    resp = deque()

def common_create_workers(func, n, *args):
    threads = []
    for i in range(n):
        t = threading.Thread(target=func, args=args)
        threads.append(t)

    t_start = time()
    for t in threads:
        t.start()

    return threads, t_start

def read_worker():
    global rw_lock, resp
    with rw_lock('r'):
        local_copy = copy(resource)
        sleep(SLEEP_TIME) # to make sure that all workers are truley accessing the resource at the same time

    resp.append(local_copy)
    return

def write_worker(val):
    global rw_lock, resource
    with rw_lock('w'):
        resource = val
    return

def test_RWLock_r():
    global rw_lock, resource, resp
    common_setup()
    resource = 0

    threads, t_start = common_create_workers(read_worker, N_WORKERS)
    for t in threads:
        t.join()
    t_end = time()
    t_diff = t_end-t_start

    assert( N_WORKERS > 2 )
    assert(t_diff < (N_WORKERS-1)*SLEEP_TIME) # for this to be true, readers have to access at same time (good)
    for r in resp:
        assert( r == resource)

def test_RWLock_w():
    global rw_lock, resource
    common_setup()
    resource = 0
    new_val = 5

    threads_w1, t_start_w1 = common_create_workers(write_worker, 1, new_val)

    for t in threads_w1:
        t.join()

    assert( resource == new_val )

def test_RWLock_rw():
    global rw_lock, resource, resp
    common_setup()
    return
    resource = 0
    soln = [0,]*N_WORKERS + [5,]*N_WORKERS

    threads_r1, t_start_r1 = common_create_workers(read_worker, N_WORKERS)
    threads_w1, t_start_w1 = common_create_workers(write_worker, N_WORKERS, 5)
    threads_r2, t_start_r2 = common_create_workers(read_worker, N_WORKERS)

    for t in threads_r1:
        t.join()
    for t in threads_w1:
        t.join()
    for t in threads_r2:
        t.join()

    for r,s in zip(resp, soln):
        assert( r == s )

def test_RWLock_timeout():
    lock = RWLock();

    assert True == lock.acquire('r', timeout=0.01)
    assert False == lock.acquire('w', timeout=0.01)
    assert True == lock.acquire('r', timeout=0.01)
    lock.release('r')
    lock.release('r')

    assert True == lock.acquire('w', timeout=0.01)
    assert False == lock.acquire('w', timeout=0.01)
    assert False == lock.acquire('r', timeout=0.01)
    lock.release('w')
   

def test_bathroom_example():
    # Note: after the janitor exits, the remaining people are nondeterministic
    sol = [
            "p_0_enter",
            "p_0_exit",
            "j_enter",
            "j_exit",
            ]

    res = bathroom_example()[:4]

    for r,s in zip(res, sol):
        assert( r == s )

def bathroom_example():
    """
    Scenario:
        A janitor needs to clean a restroom, but is not allowed to enter until
        all people are out of the restroom. How do we implement this?
    """
    restroom = RWLock()
    res = []
    n_people = 5
    sleep_time = 0.1

    def janitor():
        with restroom('w'): # block until the restroom is no longer occupied
            res.append('j_enter')
            print("(%0.3f s) Janitor  entered the restroom" % ( time() - t_start,))
            sleep(sleep_time) # clean the restroom
            res.append('j_exit')
            print("(%0.3f s) Janitor  exited  the restroom" % ( time() - t_start,))

    def people( id ):
        if id == 0: # Get the starting time of execution for display purposes
            global t_start
            t_start = time()
        with restroom('r'): # block if a janitor is in the restroom
            res.append("p_%d_enter" % (id,))
            print("(%0.3f s) Person %d entered the restroom" % ( time() - t_start, id,))
            sleep(sleep_time) # use the restroom
            res.append("p_%d_exit" % (id,))
            print("(%0.3f s) Person %d exited  the restroom" % ( time() - t_start, id,))

    people_threads = [threading.Thread(target=people, args=(i,)) for i in range(n_people)]
    janitor_thread = threading.Thread(target=janitor)

    for i, person in enumerate(people_threads):
        person.start()                 # Person i will now attempt to enter the restroom
        sleep(sleep_time * 0.6)        # wait for 60% the time a person spends in the restroom
        if i==0:                       # While the first person is in the restroom...
            janitor_thread.start()     # the janitor would like to enter. HOWEVER...
                                       # A new person (until all n_people are done) enters every 0.5 seconds.
    # Wait for all threads to finish
    for t in people_threads:
        t.join()
    janitor_thread.join()

    # The results will look like:
    """
    Running Restroom Demo
    (0.000 s) Person 0 entered the restroom
    (0.100 s) Person 0 exited  the restroom
    (0.101 s) Janitor  entered the restroom
    (0.201 s) Janitor  exited  the restroom
    (0.201 s) Person 1 entered the restroom
    (0.202 s) Person 2 entered the restroom
    (0.202 s) Person 3 entered the restroom
    (0.243 s) Person 4 entered the restroom
    (0.302 s) Person 1 exited  the restroom
    (0.302 s) Person 2 exited  the restroom
    (0.303 s) Person 3 exited  the restroom
    (0.343 s) Person 4 exited  the restroom
    """
    # While Person 0 is in the restroom, the Janitor is waiting to enter (at around 0.5000 s).
    # While the Janitor is waiting, he doesn't let anyone else into the room.
    # After Person 0, leaves the room, the Janitor enters.
    # After cleaning, the Janitor leaves at the 2.000 second mark.
    # Ever since the janitor was waiting (at 0.500 s), Person 1, Person 2, Person 3, and Person 4 have been lining up to enter.
    # Now that the Janitor left the restroom, all the waiting people go in at the same time.
    return res


if __name__ == "__main__":
    print("Running Restroom Demo")
    bathroom_example()
