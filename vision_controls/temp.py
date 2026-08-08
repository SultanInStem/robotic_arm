from pymycobot import MyCobot320Socket
mc = MyCobot320Socket("129.8.233.110", 9000)
print(mc.get_angles())