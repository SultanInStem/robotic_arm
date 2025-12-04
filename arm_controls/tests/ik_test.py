import warnings 
import numpy as np 
chain = None
with warnings.catch_warnings(): 
    warnings.simplefilter("ignore")
    from ikpy.chain import Chain
    chain = Chain.from_urdf_file("../mycobot_320pi.urdf")


x,y,z= 0.3, 0, 0.4
x1, y1, z1 = 0.011, -0.082, 0.116

current_pos_of_end_effector = [x, y, z]
orientation = [0,0,-1]
angles = chain.inverse_kinematics(current_pos_of_end_effector, orientation, orientation_mode="Z")
print("Angles: ", angles)

end_effector_frame = chain.forward_kinematics(angles)
# print(end_effector_frame)
point_in_end_effector_frame = [x1, y1, z1, 1]
# x,y,z = end_effector_frame[0][3], end_effector_frame[1][3], end_effector_frame[2][3]
point_in_base_frame = np.dot(end_effector_frame, point_in_end_effector_frame)
print("Point in base frame: ", point_in_base_frame)

current_pos_of_end_effector = np.array([x, y, z, 1])
delta_vector = point_in_base_frame - current_pos_of_end_effector
t = 1
print("New vector: ", current_pos_of_end_effector + t * delta_vector)

