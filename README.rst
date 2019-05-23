===
lox
===


.. image:: https://img.shields.io/pypi/v/lox.svg
        :target: https://pypi.python.org/pypi/lox

.. image:: https://img.shields.io/travis/BrianPugh/lox.svg
        :target: https://travis-ci.com/BrianPugh/lox

.. image:: https://readthedocs.org/projects/lox/badge/?version=latest
        :target: https://lox.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/BrianPugh/lox/shield.svg
     :target: https://pyup.io/repos/github/BrianPugh/lox/
     :alt: Updates



Threading and Multiprocessing for every project.


* Free software: MIT license
* Documentation: https://lox.readthedocs.io.

Installation
------------

    pip install git+https://github.com/BrianPugh/lox#egg=lox

Features
--------

* Powerful, intuitive multithreading in just 2 additional lines of code

* Advanced thread synchronization, communication, and resource management tools

Examples
--------

Easy Multithreading
^^^^^^^^^^^^^^^^^^^

    >>> import lox
    >>> @lox.pool(3) # Maximum of 3 concurrent threads
    >>> def multiply(a,b):
    >>>    return a*b
    >>> multiply(3,4) # Function works as normal
    12
    >>> xs = [1,2,3,4,5,]
    >>> ys = [6,7,7,8,9,]
    >>> [multiply.scatter(x,y) for x,y in zip(xs,ys)] 
    >>> multiply.gather()
    [ 6, 14, 21, 32, 45 ]


Contributing
------------
Install the library in editable mode:

    pip3 install -e .

All new features must have unit tests.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
