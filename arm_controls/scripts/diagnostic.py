import sys
import os
import time
from pymycobot.mycobot320 import MyCobot320

sys.path.append(os.path.abspath(".."))
from utils.globals import PORT, BANDWIDTH
mc = MyCobot320(PORT, BANDWIDTH)

# Give the robot a second to initialize
time.sleep(1)

# --- Check the Firmware Versions ---
print("Querying firmware versions...")

try:
    # Get the Pico version
    # 'get_system_version()' is the typical function for this
    pico_version = mc.get_system_version()
    print(f"  Pico (System) Version: {pico_version}")

    # Get the M5Stack Basic version
    basic_version = mc.get_basic_version()
    print(f"  Basic (Base) Version:    {basic_version}")

    # Get the M5Stack Atom version
    atom_version = mc.get_atom_version()
    print(f"  Atom (End) Version:      {atom_version}")

    print("\n--- Comparison ---")
    print(f"Pico:  Target was 1.5,  Found: {pico_version}")
    print(f"Basic: Target was 2.4,  Found: {basic_version}")
    print(f"Atom:  Target was 5.2,  Found: {atom_version}")

except Exception as e:
    print(f"\nAn error occurred. The robot may be in a state that")
    print(f"does not support version checking, or a firmware")
    print(f"mismatch is already preventing communication.")
    print(f"Error details: {e}")