from ikpy.chain import Chain
 

chain = Chain.from_urdf_file("mycobot_320pi.urdf")
target = [0,0,0]
angles = chain.inverse_kinematics(target)
print(angles)