lox: concurrency made easy
==========================

Many programs are `embaressingly parallel <https://en.wikipedia.org/wiki/Embarrassingly_parallel>`_ and can gain large performance boost by simply parallelizing portions of the code. However, multithreading a program is still typically seen as a difficult task and placed at the bottom of the TODO list. **lox** aims to make it as simple and intuitive as possible to parallelize functions in python. This includes both invoking functions, as well as providing easy-to-use guards for
shared resources.

**lox** provides a simple, shallow learning-curve toolset to implement multithreading or multiprocessing that will work in most projects. **lox** is not meant to be the bleeding edge of performance; for absolute maximum performance, you code will have to be more fine tuned and may benefit from python3's builtin **asyncio**, **greenlet**, or other async libraries. **lox**'s primary goal is to provide that maximum concurrency performance in the least amount of time. 

A very simple example is as follows.

.. doctest::

    >>> import lox
    >>>
    >>> @lox.thread(4) # Will operate with a maximum of 4 threads
    ... def foo(x,y):
    ...     return x*y
    >>> foo(3,4)
    12
    >>> for i in range(5):
    ...     foo.scatter(i, i+1)
    -ignore-
    >>> # foo is currently being executed in 4 threads
    >>> results = foo.gather() # block until results are ready
    >>> print(results) # Results are in the same order as scatter() calls
    [0, 2, 6, 12, 20]

Features
========

* **Multithreading**: Powerful, intuitive multithreading in just 2 additional lines of code.

* **Multiprocessing**: Truly parallel function execution with the same interface as **multithreading**.

* **Synchronization**: Advanced thread synchronization, communication, and resource management tools.

Threading vs Multiprocessing
============================

Threading has low overhead for sharing resources between threads. Threads share the same heap, meaning global variables are easily accessible from each thread. However, at any given moment, only a single line of python is being executed, meaning if your code is CPU-bound, using threading will have the same performance (actually worse due to overhead) as not using threading. 

Multiprocessing is basically several copies of your python code running at once, communicating over pipes. Each worker has it's own python interpretter, it's own stack, it's own heap, it's own everything. Any data transferred between your main program and the workers must first be serialized (using **dill**, a library very similar to **pickle**) passed over a pipe, then deserialized.

In short, if your project is I/O bound (web requests, reading/writing files, waiting for responses from compiled code/binaries, etc), threading is probably the better choice. However, if your code is computation bound, and if the libraries you are using aren't using compiled backends that are already maxing out your CPU, multiprocessing might be the better option.

Contents
========

.. toctree::
   :maxdepth: 2

   readme
   installation
   examples
   modules
   contributing
   authors
   history


Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
