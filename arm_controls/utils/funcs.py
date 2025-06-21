import warnings 
import math
chain = None
with warnings.catch_warnings(): 
    warnings.simplefilter("ignore")
    from ikpy.chain import Chain
    chain = Chain.from_urdf_file("../mycobot_320pi.urdf")

def compute_ik(point=[0,0,0.5]): # x,y,z must be in meters 
    angles = chain.inverse_kinematics(point)
    distance = point[0]**2 + point[1]**2 + point[2]**2 
    if distance > 0.5**2: 
        print("the point is out of reach")
        return [] 
        
    main_angles = []
    for i in range(1, len(angles) - 1): 
        main_angles.append(round(float(angles[i]) * (180 / math.pi), 2))
    # angles are returned in degrees 
    return main_angles
def computer_fk(): 
    pass