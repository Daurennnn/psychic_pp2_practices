class Vehicle:
  def __init__(self, brand, model):
    self.brand = brand
    self.model = model

  def move(self):
    print("Move!")

class Human:
  def __init__(self, name):
    self.name = name

class Terminator(Vehicle, Human):
    def __init__(self, brand, model, name):
        super().__init__(brand, model, name)
    def showInfo(self):
       print(self.brand, self.model, self.name)

t1000 = Terminator("scary brand", "t1000", "Arnold")