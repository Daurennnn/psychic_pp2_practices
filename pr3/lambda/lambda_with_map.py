# universal multiplier
def myfunc(n):
  return lambda a : a * n

# multiplication by 2
mydoubler = myfunc(2)
x = [1,2,3,4,5]
x_dbl = list(map(mydoubler, x))

print(x_dbl)