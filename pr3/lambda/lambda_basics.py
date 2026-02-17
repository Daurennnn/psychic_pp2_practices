# universal multiplier
def myfunc(n):
  return lambda a : a * n

# multiplication by 2
mydoubler = myfunc(2)

print(mydoubler(11))
