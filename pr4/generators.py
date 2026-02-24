# Iterator

class MyRange:
    def __init__(self, a, b, step):
        self.start = a
        self.end = b
        self.step = step

    # define iterator (return the object itself)
    def __iter__(self):
        self.x = self.start
        return self
    
    # yield next item
    def __next__(self):
        if self.x < self.end:
            item = self.x
            self.x += self.step
            return item
        else:
            raise StopIteration
        
for i in iter(MyRange(0, 101, 10)):
    print(i)


# Generator (yield outputs value while retaining function progress)
def Fibonacci(n):
    last = 1
    current = 1

    if n >= 1:
        yield last
        n -= 1

    while(n != 0):
        yield current
        temp = current
        current += last
        last = temp
        n -= 1
    
a = list(Fibonacci(10))
print(a)


# manual generator iteration

fib10 = Fibonacci(10)
print(next(fib10))
print(next(fib10))
print(next(fib10))
print(next(fib10))
print(next(fib10))
print(next(fib10))
print(next(fib10))
print(next(fib10))
print(next(fib10))
print(next(fib10))