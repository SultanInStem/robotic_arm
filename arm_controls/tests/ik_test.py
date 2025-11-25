import warnings 
import numpy as np 
chain = None
with warnings.catch_warnings(): 
    warnings.simplefilter("ignore")
    from ikpy.chain import Chain
    chain = Chain.from_urdf_file("../mycobot_320pi.urdf")




current_pos_of_end_effector = [0.3, 0, 0.4]
orientation = [0,0,-1]
angles = chain.inverse_kinematics(current_pos_of_end_effector, orientation, orientation_mode="Y")


end_effector_frame = chain.forward_kinematics(angles)
print(end_effector_frame)
point_in_end_effector_frame = [0,0,0,1]
# x,y,z = end_effector_frame[0][3], end_effector_frame[1][3], end_effector_frame[2][3]

# postion = [round(x,2), round(y,2), round(z, 2)]
# print(postion)

# rotation = end_effector_frame[:3, :3]
# for i in range(0, len(rotation)): 
    # for j in range(0, len(rotation[i])): 
        # rotation[i][j] = round(rotation[i][j], 2)
# print(end_effector_frame)
