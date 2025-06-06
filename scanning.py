from pymycobot.mycobot import MyCobot
import time

mc = MyCobot('/dev/ttyAMA0', 115200)
mc.send_angles([170,(-45),(-35),0,90,0],50)
time.sleep(3)
for count in range(2):
    mc.send_angles([170,(-45),(-35),0,20,0],50)
    time.sleep(1)
    mc.send_angles([170,(-45),(-35),0,140,0],50)
    time.sleep(1)

