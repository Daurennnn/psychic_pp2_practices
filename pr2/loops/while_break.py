from random import randint

a = randint(2, 100)
r = 1
print = True
while r < a:
    if a % r == 0:
        prime = False
    r += 1