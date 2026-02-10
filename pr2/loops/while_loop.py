from random import randint

a = randint(2, 100)
while(a != 1):
    print(a)
    if a % 2 == 0:
        a //= 2
    else:
        a = 3*a + 1
    