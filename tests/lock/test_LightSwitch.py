import threading
from lox import LightSwitch
from copy import copy
from time import sleep, time

SLEEP_TIME = 0.01
N_WORKERS = 5

common_lock = None
counting_lock = None
resp_lock = None
resource = None

def common_setup():
    global common_lock, counting_lock, resp_lock

    common_lock = threading.Lock()
    counting_lock = LightSwitch(common_lock)
    resp_lock = threading.Lock()

def test_LightSwitch_1():
    global common_lock, counting_lock, resp_lock, resource
    common_setup()

    with counting_lock:
        acquired_lock = common_lock.acquire(timeout=0)
        assert(acquired_lock == False)
    acquired_lock = common_lock.acquire(timeout=0)
    assert(acquired_lock == True)
    common_lock.release()

def test_LightSwitch_len():
    global common_lock, counting_lock, resp_lock, resource
    common_setup()
    assert( 0==len(counting_lock) )
    counting_lock.acquire()
    assert( 1==len(counting_lock) )
    counting_lock.acquire()
    assert( 2==len(counting_lock) )
    counting_lock.release()
    assert( 1==len(counting_lock) )
    counting_lock.release()
    assert( 0==len(counting_lock) )

def test_bathroom_example():
    """
    Scenario:
        A janitor needs to clean a restroom, but is not allowed to enter until
        all people are out of the restroom. How do we implement this?
    """
    restroom_occupied = threading.Lock()
    restroom = LightSwitch( restroom_occupied )

    n_people = 5

    def janitor():
        with restroom_occupied: # block until the restroom is no longer occupied
            print("(%0.3f s) Janitor  entered the restroom" % ( time() - t_start,))
            sleep(1) # clean the restroom
            print("(%0.3f s) Janitor  exited  the restroom" % ( time() - t_start,))

    def people( id ):
        if id == 0: # Get the starting time of execution for display purposes
            global t_start
            t_start = time()
        with restroom: # block if a janitor is in the restroom
            print("(%0.3f s) Person %d entered the restroom" % ( time() - t_start, id,))
            sleep(1) # use the restroom
            print("(%0.3f s) Person %d exited  the restroom" % ( time() - t_start, id,))

    people_threads = [threading.Thread(target=people, args=(i,)) for i in range(n_people)]
    janitor_thread = threading.Thread(target=janitor)

    for i, person in enumerate(people_threads):
        person.start()                 # Person i will now attempt to enter the restroom
        sleep(0.5)                     # wait for 0.5 second; a person takes 1 second in the restroom
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
    (0.502 s) Person 1 entered the restroom
    (1.001 s) Person 0 exited  the restroom
    (1.003 s) Person 2 entered the restroom
    (1.503 s) Person 1 exited  the restroom
    (1.504 s) Person 3 entered the restroom
    (2.004 s) Person 2 exited  the restroom
    (2.005 s) Person 4 entered the restroom
    (2.505 s) Person 3 exited  the restroom
    (3.006 s) Person 4 exited  the restroom
    (3.006 s) Janitor  entered the restroom
    (4.007 s) Janitor  exited  the restroom
    """
    # Note that multiple people can be in the restroom.
    # If people kept using the restroom, the Janitor would never be able
    # to enter (technically known as thread starvation).
    # If this is undesired for your application, look at OneWriterManyReader

if __name__ == "__main__":
    print("Running Restroom Demo")
    test_bathroom_example()
