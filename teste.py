import os
import subprocess

def find_mysqldump():
    for path in os.environ["PATH"].split(os.pathsep):
        mysqldump_path = os.path.join(path, "mysqldump")
        if os.path.isfile(mysqldump_path):
            return mysqldump_path
    return None

mysqldump_path = find_mysqldump()
print(mysqldump_path)