with open(r".\pr6\file_handling\subttls.txt") as file:
    print(file.read())


file = open(r".\pr6\file_handling\subttls.txt")
for i in file.readlines()[::-1]:
        print(i[:-1])
file.close()

