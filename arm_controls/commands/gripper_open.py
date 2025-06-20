import sys
import os
import time
from pymycobot.mycobot import MyCobot 
sys.path.append(os.path.abspath(".."))
from utils.compute_ik import compute_ik
from utils.globals import PORT, BANDWIDTH
mc = MyCobot(PORT, BANDWIDTH)

def open():
    mc.set_gripper_state(0, 100)
    time.sleep(2)
    return
open()

