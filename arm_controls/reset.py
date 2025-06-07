import time
from pymycobot.mycobot import MyCobot
import paramiko
mc = MyCobot('/dev/ttyAMA0', 115200)
NVIDIA_HOST = "129.8.203.200" 
NVIDIA_USER = "agxorin3"
NVIDIA_PASSWORD = "fresnostate"
# This file moves the arm back to its initial position 

def set_origin_coord(): 
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(NVIDIA_HOST, username=NVIDIA_USER, password=NVIDIA_PASSWORD)

    sftp = ssh.open_sftp()

    mc.send_angles([0,0,0,0,0,0], 50)

    while mc.is_moving(): ### Allows for the movement to finish properly
        time.sleep(0.1)

    ssh.close()
    sftp.close()
    return
set_origin_coord()