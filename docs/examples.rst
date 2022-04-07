========
Examples
========

Multithreading Requests
-----------------------

A typical usecase for **lox** is the following. Say you wanted to get the content
of websites from a list of URLs. The first naive implementation may look something
like the following.

.. doctest::

    >>> import urllib.request
    >>> from time import time
    >>> urls = ["http://google.com", "http://bing.com", "http://yahoo.com"]
    >>> responses = []
    >>>
    >>> def get_content(url):
    ...     res = urllib.request.urlopen(url)
    ...     return res.read()
    ...
    >>>
    >>> t_start = time()
    >>> for url in urls:
    ...     responses.append(get_content(url))
    ...
    >>> t_diff = time() - t_start
    >>> print("It took %.3f seconds to get 3 sites" % (t_diff,))  # doctest: +SKIP
    It took 2.942 seconds to get 3 sites

It's nice, simple, and it just works. However, your computer is just idling while
waiting for a network response. With **lox**, you can just decorate the function you
want to add concurrency. We replace the direct calls to the function with ``func.scatter`` which will pass all the ``args`` and ``kwargs`` to the decorated function. Finally, when we need all the function results, we call ``func.gather()`` which will return a list of the outputs of the decorated function. The outputs are guarenteed to be in the same order that the ``scatter`` were called

.. doctest::

    >>> import lox
    >>> import urllib.request
    >>> from time import time
    >>> urls = ["http://google.com", "http://bing.com", "http://yahoo.com"]
    >>>
    >>> @lox.thread
    ... def get_content(url):
    ...     res = urllib.request.urlopen(url)
    ...     return res.read()
    ...
    >>>
    >>> t_start = time()
    >>> for url in urls:
    ...     get_content.scatter(url)
    ...
    -ignore-
    >>> responses = get_content.gather()
    >>> t_diff = time() - t_start
    >>> print("It took %.3f seconds to get 3 sites" % (t_diff,))  # doctest: +SKIP
    It took 0.928 seconds to get 3 sites

With minimal modifications, we now have a multithreaded application with
significant performance improvements.


Multiprocessing
---------------


.. doctest::
    :skipif: True

    >>> import lox
    >>> from time import sleep
    >>>
    >>> @lox.process(2)
    ... def job(x):
    ...     sleep(1)
    ...     return 1
    ...
    >>>
    >>> t_start = time()
    >>> for i in range(5):
    ...     res = job(10)
    ...
    >>> t_diff = time() - t_start
    >>> print("Non-parallel took %.3f seconds" % (t_diff,))  # doctest: +SKIP
    Non-parallel took 5.007 seconds
    >>>
    >>> t_start = time()
    >>> for i in range(5):
    ...     job.scatter(10)
    ...
    >>> res = job.gather()
    >>> t_diff = time() - t_start
    >>> print("Parallel took %.3f seconds" % (t_diff,))  # doctest: +SKIP
    Parallel took 0.062 seconds


Obtaining a resource from a pool
--------------------------------

Imagine you have 4 GPUs that are part of a data processing pipeline, and the
GPUs perform the task disproportionally faster (or slower!) than the rest of the pipeline.
Below we have many threads fetching and processing data, but they need to share
the 4 GPUs for accelerated processing.

.. doctest::
    :skipif: True

    >>> import lox
    >>>
    >>> N_GPUS = 4
    >>> gpus = [allocate_gpu(x) for x in range(N_GPUS)]
    >>> idx_sem = lox.IndexSemaphore(N_GPUS)
    >>>
    >>> @lox.thread
    ... def process_task(url):
    ...     data = get_data(url)
    ...     data = preprocess_data(data)
    ...     with idx_sem() as idx:  # Obtains 0, 1, 2, or 3
    ...         gpu = gpus[idx]
    ...         result = gpu.process(data)
    ...     result = postprocess_data(data)
    ...     save_file(result)
    ...
    >>>
    >>> urls = [
    ...     "http://google.com",
    ... ]
    >>> for url in urls:
    ...     process_task.scatter(url)
    ...
    >>> process_task.gather()

Block until threads are done
----------------------------

Imagine the following scenario:

A janitor needs to clean a restroom, but is not allowed to enter until
all people are out of the restroom. How do we implement this?

The easiest way is to use a **lox.LightSwitch**. The lightswitch pattern
creates a first-in-last-out synchronization mechanism.
The name of the pattern is inspired by people entering a
room in the physical world. The first person to enter the room turns
on the lights; then, when everyone is leaving, the last person to exit
turns the lights off.

.. doctest::
    :skipif: True

    >>> restroom_occupied = Lock()
    >>> restroom = LightSwitch(restroom_occupied)
    >>> res = []
    >>> n_people = 5

A **LightSwitch** is most similar to a semaphore, but it automatically
acquires/releases a provided **Lock** when it's internal counter
increments/decrements from 0. A **LightSwitch** can be acquired multiple times,
but must be released the same amount of times before the **Lock** gets released.

Here's the janitor's job:

.. doctest::
    :skipif: True

    >>> @lox.thread(1)
    ... def janitor():
    ...     with restroom_occupied:  # block until the restroom is no longer occupied
    ...         res.append("j_enter")
    ...         print("(%0.3f s) Janitor  entered the restroom" % (time() - t_start,))
    ...         sleep(1)  # clean the restroom
    ...         res.append("j_exit")
    ...         print("(%0.3f s) Janitor  exited  the restroom" % (time() - t_start,))
    ...

Here are the people trying to enter the rest room:

.. doctest::
    :skipif: True

    >>> @lox.thread(n_people)
    ... def people(id):
    ...     if id == 0:  # Get the starting time of execution for display purposes
    ...         global t_start
    ...         t_start = time()
    ...     with restroom:  # block if a janitor is in the restroom
    ...         res.append("p_%d_enter" % (id,))
    ...         print(
    ...             "(%0.3f s) Person %d entered the restroom"
    ...             % (
    ...                 time() - t_start,
    ...                 id,
    ...             )
    ...         )
    ...         sleep(1)  # use the restroom
    ...         res.append("p_%d_exit" % (id,))
    ...         print(
    ...             "(%0.3f s) Person %d exited  the restroom"
    ...             % (
    ...                 time() - t_start,
    ...                 id,
    ...             )
    ...         )
    ...

Lets start these people up:

.. doctest::
    :skipif: True

    >>> for i in range(n_people):
    ...     people.scatter(i)  # Person i will now attempt to enter the restroom
    ...     sleep(0.6)  # wait for 60% the time a person spends in the restroom
    ...     if i == 0:  # While the first person is in the restroom...
    ...         janitor_thread.start()  # the janitor would like to enter. HOWEVER...
    ...         print("(%0.3f s) Janitor Dispatched" % (time() - t_start))
    ...
    >>> # Wait for all threads to finish
    >>> people.gather()
    >>> janitor.gather()

The results will look like::

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

Note that multiple people can be in the restroom.
If people kept using the restroom, the Janitor would never be able
to enter (technically known as thread starvation).
If this is undesired for your application, look at RWLock

One-Writer-Many-Reader
----------------------

It's common that many threads may be reading from a single resource, but a
single other thread may change the value of that resource.

If we used a LightSwitch as in the Janitor example above, we can see that the
writer (Janitor) may never get an opporunity to acquire the resource. A
**RWLock** solves this problem by blocking future threads from acquiring the
resource until the writer acquires and subsequently releases the resource.


.. doctest::
    :skipif: True

    >>> rwlock = lox.RWLock()

The janitor task would do something like:

.. doctest::
    :skipif: True

    >>> with rwlock('w'):
    ...     # Perform resource write here
    ...

While the people task would look like

.. doctest::
    :skipif: True

    >>> with rwlock('r'):
    ...     # Perform resource read here
    ...
