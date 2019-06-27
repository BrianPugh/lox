=======
History
=======

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
