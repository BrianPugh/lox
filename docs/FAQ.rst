===
FAQ
===

**Q: Whats the difference between multithreading and multiprocessing?**

**A:** Multithreading and Multiprocessing are two different methods to provide concurrency (parallelism) to your code.

Threading has low overhead for sharing resources between threads. Threads share the same heap, meaning global variables are easily accessible from each thread. However, at any given moment, only a single line of python is being executed, meaning if your code is CPU-bound, using threading will have the same performance (actually worse due to overhead) as not using threading.

Multiprocessing is basically several copies of your python code running at once, communicating over pipes. Each worker has it's own python interpretter, it's own stack, it's own heap, it's own everything. Any data transferred between your main program and the workers must first be serialized (using **dill**, a library very similar to **pickle**) passed over a pipe, then deserialized.

In short, if your project is I/O bound (web requests, reading/writing files, waiting for responses from compiled code/binaries, etc), threading is probably the better choice. However, if your code is computation bound, and if the libraries you are using aren't using compiled backends that are already maxing out your CPU, multiprocessing might be the better option.

**Q: Why not just use the built-in** ``await`` **?**

**A:** Trying to shove ``await`` into a project typically requires great care both in the code written and the packages used. Ontop of this, using await may require a substantial refactor of the layout of the code. The goal of **lox** is to require the smallest, least risky changes in your codebase.
