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
from commands.main import reset, move_to_location, close_gripper, open_gripper,  get_arms_angles, set_arms_angles
from utils.funcs import compute_ik, compute_fk
from utils.globals import PORT, BANDWIDTH
mc = MyCobot320(PORT, BANDWIDTH)

deposit_angles = [0, 0.566, 0, 0.979, -1.57, 0]



def scanning_table(): 
    initial_angles = [-0.58,  -0.864, 0, -0.685,  1.57,  0] 
    final_angles = [0.7,  -0.864, 0, -0.685,  1.57,  0]
    set_arms_angles(initial_angles, 10)
    while mc.is_moving(): ### Allows for the movement to finish properly
        time.sleep(0.1)
    time.sleep(2)
    set_arms_angles(final_angles, 10)
    while mc.is_moving(): ### Allows for the movement to finish properly
        time.sleep(0.1)
    time.sleep(2)

    target_angles = [0.32, -1.04, 0, -0.522, 1.57, 0]
    set_arms_angles(target_angles, 10)
    while mc.is_moving(): ### Allows for the movement to finish properly
        time.sleep(0.1)
    time.sleep(1)

    close_gripper()
    time.sleep(1) 
    set_arms_angles(deposit_angles, 10)
    while mc.is_moving(): ### Allows for the movement to finish properly    
        time.sleep(0.1)
    time.sleep(1)
    open_gripper()
    time.sleep(1)
    reset()
# scanning_table()


def scanning_tree(): 
    initial_angles = [1, 1.3, 0, -1.4, 0.5,  0]
    final_angles =   [1, 1.3, 0, -1.4, 1.55, 0]
    target_angles = [0.18, -0.917, 0, -2.21, -2.93,  3.14]
    # set_arms_angles(initial_angles, 10)
    while mc.is_moving(): ### Allows for the movement to finish properly
        time.sleep(0.1)
    # time.sleep(2)
    # set_arms_angles(final_angles, 10)
    while mc.is_moving(): ### Allows for the movement to finish properly
        time.sleep(0.1)
    # time.sleep(2)
    set_arms_angles(target_angles, 10)
    while mc.is_moving(): ### Allows for the movement to finish properly
        time.sleep(0.1)
    time.sleep(1)
    close_gripper()
    time.sleep(1)
    set_arms_angles(deposit_angles, 10)
    while mc.is_moving(): ### Allows for the movement to finish properly    
        time.sleep(0.1)
    time.sleep(1)
    open_gripper()
    time.sleep(1)
    reset()

scanning_tree()

