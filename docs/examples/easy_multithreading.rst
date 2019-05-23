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

