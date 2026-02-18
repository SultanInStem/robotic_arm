import sys
import os
import numpy as np
import numpy as np
import time
from pymycobot.mycobot320 import MyCobot320
sys.path.append(os.path.abspath(".."))
from commands.main import reset, move_to_location, close_gripper, open_gripper,  get_arms_angles
from utils.funcs import compute_ik, compute_fk, convert_to_radians, convert_point_from_end_effector_to_base_frame
from utils.globals import PORT, BANDWIDTH
mc = MyCobot320(PORT, BANDWIDTH)


move_to_location([0.3, 0.2, 0.1], 30)
time.sleep(1)
close_gripper()
move_to_location([-0.3, 0.2, 0.2], 10)
time.sleep(1)
open_gripper()
