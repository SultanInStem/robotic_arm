import sys
import os
import time
from pymycobot.mycobot import MyCobot 
sys.path.append(os.path.abspath(".."))
from utils.compute_ik import compute_ik
from utils.globals import PORT, BANDWIDTH


def move_to_location(point, speed): 
    mc = MyCobot(PORT, BANDWIDTH)
    angles = compute_ik(point)
    if len(angles) < 6: return -1
    elif speed > 90: 
        print("speed must not exceed 90")
        return -1
    mc.send_angles(angles, speed)
    while mc.is_moving():
        time.sleep(0.1)
    time.sleep(2)
    return 0
     

