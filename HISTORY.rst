=======
History
=======

0.10.0 (2021-12-18)
-------------------
* Remove dependency pinning.
* Allow `@lox.thread(0)`. This will execute `scatter` calls in parent thread.
  Useful for debugging breakpoints in parallelized code.

0.9.0 (2020-11-25)
------------------
* ``tqdm`` support on ``lox.process.gather``. See v0.8.0 release notes for usage.

0.8.0 (2020-11-25)
------------------
* ``tqdm`` support on ``lox.thread.gather``
  * Can be a bool::

        >>> my_func.gather(tqdm=True)

  * Can be a ``tqdm`` object::

        >>> from tqdm import tqdm
        >>> pbar = tqdm(total=100)
        >>> for _ in range(100):
        >>>     my_func.scatter()
        >>> my_func.gather(tqdm=pbar)

0.7.0 (2020-07-20)
------------------
* Complete rework of workers
  + Fix memory leaks
* Drop support for python3.5
* Drop support for chaining in favor of simpler codebase

0.6.3 (2019-07-30)
------------------
* Alternative fix for 0.6.2.

0.6.2 (2019-07-21)
------------------
* Update dependencies
* Fix garbage-collecting exclusiviity

0.6.1 (2019-07-21)
------------------
* Fix memory leak in ``lox.process``.

0.6.0 (2019-07-21)
------------------

* ``lox.Announcement`` ``subscribe()`` calls now return another ``Announcement``
  object that behaves like a queue instead of an actual queue. Allows for
  many-queue-to-many-queue communications.

* New Object: ``lox.Funnel``. allows for waiting on many queues for a complete
  set of inputs indicated by a job ID.

0.5.0 (2019-07-01)
------------------

* New Object: ``lox.Announcement``. Allows a one-to-many thread queue with
  backlog support so that late subscribers can still get all (or most recent)
  announcements before they subscribed.

* New Feature: ``lox.thread``  ``scatter`` calls can now be chained together.
  ``scatter`` now returns an ``int`` subclass that contains metadata to allow
  chaining. Each scatter call can have a maximum of 1 previous ``scatter`` result.

* Documentation updates, theming, and logos

0.4.3 (2019-06-24)
------------------
* Garbage collect cached decorated object methods

0.4.2 (2019-06-23)
------------------
* Fixed multiple instances and successive scatter and gather calls to wrapped methods

0.4.1 (2019-06-23)
------------------
* Fixed broken workers and unit tests for workers

0.4.0 (2019-06-22)
------------------
* Semi-breaking change: **lox.thread** and **lox.process** now automatically pass
  the object instance when decorating a method.

0.3.4 (2019-06-20)
------------------
* Print traceback in red when a thread crashes

0.3.3 (2019-06-19)
------------------
* Fix bug where thread in scatter of lox.thread double releases on empty queue

0.3.2 (2019-06-17)
------------------

* Fix manifest for installation from wheel

0.3.1 (2019-06-17)
------------------

* Fix package on pypi

0.3.0 (2019-06-01)
------------------

* Multiprocessing decorator. **lox.pool** renamed to **lox.thread**

* Substantial pytest bug fixes

* Documentation examples

* timeout for RWLock

0.2.1 (2019-05-25)
------------------

* Fix IndexSemaphore context manager

0.2.0 (2019-05-24)
------------------

* Added QLock

* Documentation syntax fixes

0.1.1 (2019-05-24)
------------------

* CICD test

0.1.0 (2019-05-24)
------------------

* First release on PyPI.
