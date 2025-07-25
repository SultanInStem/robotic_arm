import warnings 
import numpy as np 
chain = None
with warnings.catch_warnings(): 
    warnings.simplefilter("ignore")
    from ikpy.chain import Chain
    chain = Chain.from_urdf_file("../mycobot_320pi.urdf")




target = [-0.4, 0, 0]
angles = chain.inverse_kinematics(target)
for i in range(0, len(angles)): 
    angles[i] = round(angles[i], 2)
# angles = angles[1:7]
print(angles)


end_effector_frame = chain.forward_kinematics(angles)
x,y,z = end_effector_frame[0][3], end_effector_frame[1][3], end_effector_frame[2][3]

postion = [round(x,2), round(y,2), round(z, 2)]
print(postion)

rotation = end_effector_frame[:3, :3]
for i in range(0, len(rotation)): 
    for j in range(0, len(rotation[i])): 
        rotation[i][j] = round(rotation[i][j], 2)
# print(end_effector_frame)
