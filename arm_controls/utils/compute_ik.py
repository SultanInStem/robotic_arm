import warnings 
import math
chain = None
with warnings.catch_warnings(): 
    warnings.simplefilter("ignore")
    from ikpy.chain import Chain
    chain = Chain.from_urdf_file("../mycobot_320pi.urdf")

def compute_ik(x=0,y=0,z=0.5): # x,y,z must be in meters 
    angles = chain.inverse_kinematics([x,y,z])
    distance = x**2 + y**2 + z**2 
    if distance > 0.5**2: 
        print("the point is out of reach")
        return [0,0,0,0,0,0] 
        
    main_angles = []
    for i in range(1, len(angles) - 1): 
        main_angles.append(round(float(angles[i]) * (180 / math.pi), 2))
    # angles are returned in degrees 
    print(main_angles)    
    return main_angles
