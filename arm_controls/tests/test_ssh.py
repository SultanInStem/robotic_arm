import paramiko 
import sys
import os 
sys.path.append(os.path.abspath(".."))
from utils.globals import NVIDIA_HOST, NVIDIA_PASSWORD, NVIDIA_USER



ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(NVIDIA_HOST, username=NVIDIA_USER, password=NVIDIA_PASSWORD, look_for_keys=False, allow_agent=False)
COORD_FILE = "/home/usr2/Desktop/missed_me.txt"
sftp = ssh.open_sftp()
try:
    with sftp.open(COORD_FILE, "w") as f:
        f.write("hello world")
except FileNotFoundError:
        pass

sftp.close()
ssh.close()
