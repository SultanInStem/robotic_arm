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
from utils.funcs import compute_ik, compute_fk
from utils.globals import PORT, BANDWIDTH
mc = MyCobot320(PORT, BANDWIDTH)

degree = 180 / math.pi

# tree_angles = [1.64,-0.76,-0.52,1.41,0,0]


def scanning_table(): 
    initial_angles = [-0.58 * degree,  -0.864 * degree, 0, -0.685 * degree,  1.57 * degree,  0] 
    final_angles = [0.7 * degree,  -0.864 * degree, 0, -0.685 * degree,  -1.57 * degree,  0]
    mc.send_angles(initial_angles, 10)
    while mc.is_moving(): ### Allows for the movement to finish properly
        time.sleep(0.1)
    time.sleep(2)
    mc.send_angles(final_angles, 10)
    while mc.is_moving(): ### Allows for the movement to finish properly
        time.sleep(0.1)
    time.sleep(2)

scanning_table()


def scanning_tree(): 
    pass
