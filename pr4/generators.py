# Iterator

class MyRange:
    def __init__(self, a, b, step):
        self.a = a
        self.b = b
        self.step = step

    def __iter__(self):
        self.x = self.a
        return self
    
    def __next__(self):
        if self.a < self.b:
            x = self.a
            self.a += self.step
            return x
        else:
            raise StopIteration
        
for i in iter(MyRange(0, 101, 10)):
    print(i)


# Generator (each yield is called implicitly using __next__())
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