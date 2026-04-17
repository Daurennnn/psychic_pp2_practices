import os
import shutil

path = r"./pr6/file_handling/subttls.txt"
backup = r"./pr6/file_handling/backup"


if os.path.exists(path):

    if not os.path.exists(backup):
        os.mkdir(backup)
    
    shutil.copy(path, backup + r"/subttls_copy")
    os.remove(path)

    if not os.path.exists(path): print("File deleted")
else:
    print("The file does not exist")