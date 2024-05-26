from wahoo_device import *
from time import sleep

"""
BEFORE RUNNING ANY TEST:
    - Add the root path stuff to each file
    - Put all the files into a nice folder
    - Add tests for just bike data reading
    - Add tests for just resistance
    - Add test for both resistance and data
    - Add test for all - resistance, data & incline
"""

"""Possibility that initialising the manager per a device may not work"""
if True:
    # Test connecting to Climber
    incline = InclineDevice()

if True:
    # Test setting safe incline values
    incline = InclineDevice()
    incline.custom_control_point_set_target_inclination(10)
    sleep(8)
    incline.custom_control_point_set_target_inclination(-5)
    sleep(8)

if True:
    # Test setting max & min incline values
    incline = InclineDevice()
    incline.custom_control_point_set_target_inclination(19)
    sleep(8)
    incline.custom_control_point_set_target_inclination(-10)
    sleep(8)
