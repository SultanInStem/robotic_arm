from pymycobot.mycobot import MyCobot
import time

mc = MyCobot('/dev/ttyAMA0', 115200)
def starting_pos():
    mc.send_angles([0,0,0,0,0,0],50)
    time.sleep(1)
    mc.send_angles([170,(-45),(-35),0,90,0],50)
    time.sleep(1)
    mc.set_gripper_state(1, 100)
    time.sleep(1)
    
starting_pos()
