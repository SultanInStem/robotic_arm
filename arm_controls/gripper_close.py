from pymycobot.mycobot import MyCobot
import pymycobot
import time
mc = MyCobot('/dev/ttyAMA0', 115200)


def close():
    grip_value = mc.set_gripper_state(1, 70)
    print(grip_value)
    time.sleep(4)
    return
close()