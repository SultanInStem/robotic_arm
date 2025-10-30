import warnings 
import math
chain = None
with warnings.catch_warnings(): 
    warnings.simplefilter("ignore")
    from ikpy.chain import Chain
    chain = Chain.from_urdf_file("../mycobot_320pi.urdf")

def compute_ik(point=[0,0,0.5], orientation=[0,-1,0]): # x,y,z must be in meters 
    angles = chain.inverse_kinematics(point, orientation, orientation_mode="Y")
    distance = point[0]**2 + point[1]**2 + point[2]**2 
    if distance > 0.5**2: 
        print("the point is out of reach")
        return [] 
        
    main_angles = []
    for i in range(1, len(angles) - 1): 
        main_angles.append(round(float(angles[i]) * (180 / math.pi), 2))
    # angles are returned in degrees 
    return main_angles
def compute_fk(angles): # angles must contain 8 items in radians!!!
    end_effector_frame = chain.forward_kinematics(angles)
    x,y,z = end_effector_frame[0][3], end_effector_frame[1][3], end_effector_frame[2][3]
    position = [round(x,2),round(y,2),round(z,2)]
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