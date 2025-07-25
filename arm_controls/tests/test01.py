import time 
# import paramiko 
from pymycobot.mycobot import MyCobot
import sys
import os
sys.path.append(os.path.abspath(".."))
# from commands.main import reset, compute_fk
from utils.funcs import compute_fk, get_rotation_matrix

COORD_FILE = "/Desktop/robotic_arm/vision_controls/CNN/strawberry_coords.txt"

### PSEUDO CODE 
# 1) Look around for a strawberry 
# if nothing is found, go the original position and stop 
# 2) Locate the strawberry  
# 3) Pick the strawberry 
# 4) Deposit the strawberry
# 5) Repeat
###

# mc = MyCobot('/dev/ttyAMA0', 115200)
# compute_fk([0,0,0,0,0,0,0,0])

def look_around():
    z_levels = [0.5, 0.4, 0.3, 0.2]
    # the arm does 360 around it origin at specified z_levels
    for i in range(len(z_levels)):
        print(i)
        # go to i'th z-level at the same (x,y)
        # rotate the first joint 
        # repeat 



    return False    
        

# ----------- MAIN LOOP --------- 
is_running = True 
# reset() ### set the arm to the origin b4 running the loop
while(is_running): 

    is_running = look_around()

    pass
