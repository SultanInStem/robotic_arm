import sys
import os
import paramiko 
import time
from pymycobot.mycobot320 import MyCobot320
sys.path.append(os.path.abspath(".."))
from commands.main import reset, move_to_location, close_gripper, open_gripper, get_arms_orientation
from utils.funcs import compute_ik, compute_fk, convert_to_radians, convert_point_from_end_effector_to_base_frame
from utils.globals import PORT, BANDWIDTH
mc = MyCobot320(PORT, BANDWIDTH)

HOST = "192.168.10.1"
port = 22
username = "usr2" # username of nvidia jetson 
password = "fresnostate" # password of nvidia jetson
remote_file_path = "/home/usr2/robotic_arm/vision_controls/AI_model/coords_data.txt"


# reset() # Reset the robot to the initial position


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
def connect_ssh(): 
    try:   
        ssh.connect(HOST, port, username, password)
        sftp = ssh.open_sftp()
        print("Connection established.")
        with sftp.open(remote_file_path, 'a') as f:
            f.write("This line is written from the Pi!\n")
            f.write(f"Sensor Value: {1024}\n")

        print("Text appended successfully.")
    except Exception as e:
        print(f"Connection failed: {e}")
    return ssh, sftp


connect_ssh()



# while True: 
    # coords_in_end_effector_frame = []






