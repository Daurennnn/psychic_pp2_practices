class Job:
    def __init__(self, title, salary):
        self.title = title
        self.salary = salary
    
    def display(self):
        print("Title:", self.title)
        print(f"Salary: {self.salary}$")

job1 = Job("Plumber", 1000)
job1.display()