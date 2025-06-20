import sys
import os
from pymycobot.mycobot import MyCobot 
sys.path.append(os.path.abspath(".."))
from utils.compute_ik import compute_ik
from utils.globals import PORT, BANDWIDTH


def move_to_location(point, speed): 
    mc = MyCobot(PORT, BANDWIDTH)
    angles = compute_ik(point)
    if len(angles) < 6: return 
    mc.send_angles(angles,)
