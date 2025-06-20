from pymycobot.mycobot import MyCobot 
from ikpy.chain import Chain
import time
mc = MyCobot('/dev/ttyAMA0', 115200) 


def main(): 
    x = float(input("Enter x(meters): "))
    y = float(input("Enter y(meters): "))
    z = float(input("Enter z(meters): "))
    chain = Chain.from_urdf_file("mycobot_320pi.urdf")
    target = [x,y,z]
    angles = chain.inverse_kinematics(target)
    angles = angles[1:7]
    main_angles = []
    factor = 180 / 3.145
    for i in range(0, len(angles)): 
        main_angles.append(float(angles[i])*factor)
    mc.send_angles(main_angles, 10)
    while mc.is_moving(): 
        time.sleep(0.1)
    time.sleep(2)
    main_angles.insert(0,0)
    main_angles.append(0)
    gripper_matrix = chain.forward_kinematics(main_angles)
    print(gripper_matrix)

main()



