class Person:
  count = 0  # static variable = class variable
  def __init__(self, name, age):
    self.name = name
    self.age = age
    self.count += 1

p1 = Person("Emil", 36)

print(p1.name)
print(p1.age)
print(p1.count)