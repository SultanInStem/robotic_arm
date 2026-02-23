import sys
import os
import numpy as np
import paramiko
import time
import warnings 
import math
import numpy as np
chain = None
with warnings.catch_warnings(): 
    warnings.simplefilter("ignore")
    from ikpy.chain import Chain
    chain = Chain.from_urdf_file("../mycobot_320pi.urdf")
from pymycobot.mycobot320 import MyCobot320
sys.path.append(os.path.abspath(".."))
from commands.main import reset, move_to_location, close_gripper, open_gripper,  get_arms_angles
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
        orientation = [0,0,-1]
        current_pos_of_end_effector = []
        with open("../../current_location.txt", "r") as f:
            content = f.read()
            current_pos_of_end_effector = [float(x) for x in content.split(",")]
        current_angles = chain.inverse_kinematics(current_pos_of_end_effector, [0,0,-1], orientation_mode="Z")
        coords.append(1) # add 1 to make dimensions compatible for matrix multiplication
        base_frame_coords = convert_point_from_end_effector_to_base_frame(coords, current_angles)
        if base_frame_coords[2] < 0.10:
            print("Object is too close to the base frame.")
            base_frame_coords[2] = 0.10 # set a minimum height for the object to be picked up
        move_to_location(base_frame_coords, 10)
        time.sleep(2)
        close_gripper()
        move_to_location([-0.3,0,0.2], 20)
        time.sleep(2)
        open_gripper()        
        print("Moving to object... ", base_frame_coords)
        reset()
        break
      

    










