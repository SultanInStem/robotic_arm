import sys
import os
import time
from pymycobot.mycobot320 import MyCobot320
sys.path.append(os.path.abspath(".."))
from commands.main import reset, move_to_location, close_gripper, open_gripper
from utils.funcs import compute_ik, compute_fk, convert_to_radians
from utils.globals import PORT, BANDWIDTH
mc = MyCobot320(PORT, BANDWIDTH)

reset()
move_to_location([0.3, 0, 0.1], 20)
close_gripper()
move_to_location([-0.3, 0, 0.2], 20) 
open_gripper()
reset()
