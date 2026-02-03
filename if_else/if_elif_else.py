from random import randint

age = randint(0, 9999)

if(age > 5000):
    print("You are old enough")
elif(age > 2000):
    print("You are a baby")
else:
    print("You are an infant")