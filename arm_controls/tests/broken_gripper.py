from pymycobot import MyCobot320
import time 
from pymycobot import __version__

print(__version__)
mc = MyCobot320('/dev/ttyAMA0', 115200, debug=True)

coords = mc.get_coords()
time.sleep(0.1)
print(coords)