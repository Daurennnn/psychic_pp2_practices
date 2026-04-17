import os
import shutil

root = "./pr6/directory_management"
name = "invitation"
    
os.chdir(root)
with open(name + ".txt", 'wt') as file:
    file.write("Come to my bd tomorrow!")

dest = input("Destination folder name: ")
if not os.path.exists(dest):
    os.mkdir(dest)
    
shutil.move(name + ".txt", dest + "/" + name)