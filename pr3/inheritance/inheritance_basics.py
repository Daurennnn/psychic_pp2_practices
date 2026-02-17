class Person:
  def __init__(self, fname, lname):
    self.firstname = fname
    self.lastname = lname

  def printname(self):
    print(self.firstname, self.lastname)

class Student(Person):
  def __init__(self, fname, lname, grade):
    self.firstname = fname
    self.lastname = lname
    self.grade = grade

pers1 = Person("Temirlan", "K.")
stud1 = Student("Dauren", "Zh.", 1)
