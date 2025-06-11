from pymycobot.mycobot320 import MyCobot320

import time 

mc = MyCobot320("/dev/ttyAMA0", 115200)

mc.send_angle([-0.2,0,0,0,0,0], 70)
time.sleep(2)
print("DONE")