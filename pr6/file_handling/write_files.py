with open(r".\pr6\file_handling\subttls.txt", 'wt') as file:
    file.write('''
               Hello, this lecture is about chain fractions
               First we will discuss Euler method for GCD
               Then I will show its applications
               ''')


with open(r".\pr6\file_handling\subttls.txt", 'at') as file:
    file.write("This is going to be an interesting presentation!\n")