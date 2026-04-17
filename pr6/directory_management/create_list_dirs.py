import os
import re

directory = r"./pr6/directory_management"

os.chdir(directory)

print("Listing python files")
for i in os.listdir():
    if re.match(r".*\.py", i):
        print("  -{0}".format(i))
print()

print("Listing non python files and folders")
for i in os.listdir():
    if not re.match(r".*\.py", i):
        print("  -{0}".format(i))
print()

dir_parent = input("enter parent directory name: ")
dir_names = input("enter new folder names separated by spaces: ").split()

if not os.path.exists(dir_parent):
    os.mkdir(dir_parent)

os.chdir(dir_parent)

for dir in dir_names:
    os.mkdir(dir)