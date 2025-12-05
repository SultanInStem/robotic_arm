import sys
import os
import numpy as np
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

def connect_ssh(): 
    ssh = paramiko.SSHClient()
    try:   
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, port, username, password)
        sftp = ssh.open_sftp()
        print("Connection established.")
    except Exception as e:
        print(f"Connection failed: {e}")
    return ssh, sftp

ssh, sftp = connect_ssh()

def fetch_coordinates(): 
    with sftp.open(remote_file_path, 'r') as f:
        bytes = f.read()
        content = bytes.decode('utf-8')
        if not content: 
            return []
        coords_from_cam = [float(x.strip()) for x in content.split(",") if x.strip()]
        print("Coordinates from camera: ", coords_from_cam)
        return coords_from_cam
    return []


# fetch_coordinates()

reset()
while True:
    scanning = True
    initial_position = np.array([0.3,-0.2,0.3])
    final_position = np.array([0.3,0.2,0.3])
    location = initial_position.copy()
    step_size = 0.05
    
    while scanning:
        move_to_location(location, 20)
        print("Location ", location)
        
        time.sleep(3) # wait for the camera to process and write the file
        coords = fetch_coordinates()
        if len(coords) == 3:
            print("Object detected at: ", coords)
            scanning = False
            break


        if location[1] < final_position[1]:
            location[1] += step_size
        else:
            location[1] = initial_position[1]
            move_to_location(location, 20)

    if scanning == False:
        
        print("Moving to object... ", coords)
        break

    










