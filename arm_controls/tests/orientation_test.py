from pymycobot.mycobot import MyCobot 
from ikpy.chain import Chain
import time
mc = MyCobot('/dev/ttyAMA0', 115200) 

def main(): 
    chain = Chain.from_urdf_file("mycobot_320pi.urdf")
    target = [0.4,0, 0.1]
    angles = chain.inverse_kinematics(target)
    angles = angles[1:7]
    main_angles = []
    factor = 180 / 3.145
    for i in range(0, len(angles)): 
        main_angles.append(float(angles[i])*factor)
    mc.send_angles(main_angles, 10)
    angles = [0.12, -1.70, -0.05, -0.36, -2.15, -1.6]
    mc.send_angles(angles, 10)
    while mc.is_moving(): 
        time.sleep(0.1)



