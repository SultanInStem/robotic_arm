import warnings 
import math
import numpy as np
chain = None
with warnings.catch_warnings(): 
    warnings.simplefilter("ignore")
    from ikpy.chain import Chain
    chain = Chain.from_urdf_file("../mycobot_320pi.urdf")
### The orientaton facing the table downwards is [0,0,-1] in Z direction
def compute_ik(point=[0.3,0,0.4], orientation=[0,0,-1], orientation_mode="Z"): # x,y,z must be in meters 
    angles = chain.inverse_kinematics(point, orientation, orientation_mode)
    distance = point[0]**2 + point[1]**2 + point[2]**2 
    if distance > 0.5**2: 
        print("the point is out of reach")
        return [] 
    main_angles = []
    for i in range(1, len(angles) - 1): 
        main_angles.append(round(float(angles[i]) * (180 / math.pi), 2))
    # angles are returned in degrees 
    return main_angles
def convert_point_from_end_effector_to_base_frame(point_in_end_effector_frame, angles): # current angles of the arm
    end_effector_frame = chain.forward_kinematics(angles)
    point_in_base_frame = np.dot(end_effector_frame, point_in_end_effector_frame)
    x, y, z = point_in_base_frame[0], point_in_base_frame[1], point_in_base_frame[2]
    position = [round(x,5), round(y,5), round(z,5)]
    return position


def compute_fk(angles): # angles must contain 8 items in radians!!!
    end_effector_frame = chain.forward_kinematics(angles)
    x,y,z = end_effector_frame[0][3], end_effector_frame[1][3], end_effector_frame[2][3]
    position = [round(x,5),round(y,5),round(z,5)]
    return position


# Rotation matrix that translates from end_effector_frame to base_frame
def get_rotation_matrix(angles): ## must contain 8 angles in radians
    end_effector_frame = chain.forward_kinematics(angles)
    rotation = end_effector_frame[:3, :3]
    for i in range(0, len(rotation)): 
        for j in range(0, len(rotation[i])): 
            rotation[i][j] = round(rotation[i][j], 2)
    return rotation


def convert_to_radians(n): 
    return round(n * (math.pi / 180), 2)


