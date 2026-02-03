from random import randint

testosterone = randint(0, 999)

print("You are probably a", "male" if testosterone > 100 else "female")
