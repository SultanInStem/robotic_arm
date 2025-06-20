from ikpy.chain import Chain
 

chain = Chain.from_urdf_file("mycobot_320pi.urdf")
target = [0,0, 0]
angles = chain.inverse_kinematics(target)
# angles = angles[1:7]


# Position: x = -0.050, y = -0.148, z = 0.503

end_effector_frame = chain.forward_kinematics(angles)
print(end_effector_frame)
rotation = end_effector_frame[:3, :3]
print(rotation)
# print(f"Position: x = {x:.3f}, y = {y:.3f}, z = {z:.3f}")