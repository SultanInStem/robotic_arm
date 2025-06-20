from pymycobot.mycobot import MyCobot 
from ikpy.chain import Chain
import time
 
mc = MyCobot("/dev/ttyAMA0", 115200) 


def main(): 
    angles = [0.12, -1.70, -0.05, -0.36, -2.15, -1.6]
    mc.send_angles(angles, 10)
    while mc.is_moving(): 
        time.sleep(0.1)
    time.sleep(2)
    print("Frame of the last joint: " )
    print(mc.get_coords())

main()



# Position: x = -0.050, y = -0.148, z = 0.503

# end_effector_frame = chain.forward_kinematics([0,0,0,0,0,0,0,0])
# x, y, z = end_effector_frame[:3, 3]
# print(f"Position: x = {x:.3f}, y = {y:.3f}, z = {z:.3f}")