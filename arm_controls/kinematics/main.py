import warnings 
import numpy as np

chain = None
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from ikpy.chain import Chain
    chain = Chain.from_urdf_file(
        "./mycobot_320pi.urdf",
        active_links_mask=[False, True, True, True, True, True, True, False]
    )


