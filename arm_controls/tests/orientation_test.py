from pymycobot.mycobot import MyCobot 
from ikpy.chain import Chain
import time
mc = MyCobot('/dev/ttyAMA0', 115200) 


def main(): 
    mc.send_angles([0.12, -1.70, -0.05, -0.36, -2.15, -1.6], 20)
    while mc.is_moving(): 
        time.sleep(0.1)
    time.sleep(2)
    print("Frame of the last joint: " )
    print(mc.get_coords())
main()



