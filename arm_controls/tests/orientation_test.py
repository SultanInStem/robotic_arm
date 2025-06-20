from pymycobot.mycobot import MyCobot 
from ikpy.chain import Chain
import time
 
mc = MyCobot("/dev/ttyAMA0", 115200) 


def main(): 
    chain = Chain.from_urdf_file("mycobot_320pi.urdf")
    target = [0.4,0, 0.1]
    angles = chain.inverse_kinematics(target)
    angles = angles[1:7]
    main_angles = []
    for i in range(0, len(angles)): 
        main_angles.append(float(angles[i]))
    print(type(main_angles))
    mc.send_angles(main_angles, 10)
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