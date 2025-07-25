import time 
import paramiko 
from pymycobot.mycobot import MyCobot
import sys
import os
import numpy as np
sys.path.append(os.path.abspath(".."))
from commands.main import reset
from utils.funcs import get_rotation_matrix, compute_ik
from utils.globals import NVIDIA_HOST, NVIDIA_PASSWORD, NVIDIA_USER

mc = MyCobot('/dev/ttyAMA0', 115200)



COORD_FILE = "/Desktop/robotic_arm/vision_controls/CNN/strawberry_coords.txt"
ready_angles = [-10, 25, 55, 0, -90, 0]
deposit_angles = [65, -90, 90, 45, -90, 0]

def clean_strawberry_coords():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(NVIDIA_HOST, username=NVIDIA_USER, password=NVIDIA_PASSWORD)

    sftp = ssh.open_sftp()
    try:
        with sftp.open(COORD_FILE, "w") as f:
            f.write("")
    except FileNotFoundError:
        pass

    sftp.close()
    ssh.close()

def fetch_strawberry_coords():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(NVIDIA_HOST, username=NVIDIA_USER, password=NVIDIA_PASSWORD)

    sftp = ssh.open_sftp()
    try:
        with sftp.open(COORD_FILE, "r") as f:
            coords = f.readlines()
    except FileNotFoundError:
        coords = []

    sftp.close()
    ssh.close()
    print("STRAWBERRY: ")
    print(coords)
    return coords



def go_to_ready(): 
    time.sleep(1)
    angles = [(-10),25,55,0,(-90),0]
    mc.send_angles(ready_angles, 30)
 
def deposit():
    mc.send_angles(deposit_angles, 40)
    time.sleep(4)
    mc.set_gripper_state(0, 60)  # Open gripper
    time.sleep(1)

# ----------- MAIN LOOP --------- 
reset() ### set the arm to the origin b4 running the loop
i = 0
N = 10
while(i < N):
    coords = fetch_strawberry_coords() # [x,y,z]
    # might have to negate one of the coordinates 
    if not len(coords):
        print("No strawberries detected.")
        i += 1
        continue
    coords = np.array(coords) # convert into numpy vector 
    # coords is in end_effector_frame so we should translate it to base_frame 
    rotation_matrix = get_rotation_matrix(ready_angles)
    straw_pos = rotation_matrix @ coords
    target_angles = compute_ik(straw_pos)
    mc.send_angles(target_angles, 30)  
    time.sleep(1)
    mc.set_gripper_state(1, 60)
    time.sleep(1)
    deposit()
    clean_strawberry_coords()
    go_to_ready()

reset()



