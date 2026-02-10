def gurtYo(age, *hobbies, **people):
    print(f"I am {age} years old.")

    print("I like ", end="")
    for i in hobbies:
        print(i, end="")
    print(".")

    for a, b in people.items():
        print(f"{a} is my {b}.")


age = 12
hobbies = ["volleyball", "coding", "drawing", "reading"]
people = {
    "Gurt" : "friend",
    "Yo" : "girlfriend"
}

gurtYo(age, *hobbies, **people)