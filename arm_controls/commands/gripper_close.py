import time
import sys 
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from globals import mc

def close():
    mc.set_gripper_state(1, 70)
    time.sleep(4)
    return
close()