from pymycobot.mycobot import MyCobot

import time 

mc = MyCobot("/dev/ttyAMA0", 115200)

mc.send_angle([-0.2,0,0,0,0,0], 70)
time.sleep(2)
print("DONE")