import warnings 
chain = None
with warnings.catch_warnings(): 
    warnings.simplefilter("ignore")
    from ikpy.chain import Chain
    chain = Chain.from_urdf_file("mycobot_320pi.urdf")




target = [-0.050, -0.148, 0.503]
angles = chain.inverse_kinematics(target)
# angles = angles[1:7]

# to go from the coordinate system of the gripper 
# to the coordinate system of the base 
# we must multiply a vector by the inverse of rotation matrix

# Position: x = -0.050, y = -0.148, z = 0.503

end_effector_frame = chain.forward_kinematics(angles)
rotation = end_effector_frame[:3, :3]
for i in range(0, len(rotation)): 
    for j in range(0, len(rotation[i])): 
        rotation[i][j] = round(rotation[i][j], 2)
print(rotation)
# print(f"Position: x = {x:.3f}, y = {y:.3f}, z = {z:.3f}")