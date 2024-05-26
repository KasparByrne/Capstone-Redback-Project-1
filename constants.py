# Fitness Machine Service (FTMS)
FTMS_UUID = 0x1826

# Fitness Machine Control Point Op Codes (more details in https://www.bluetooth.com/specifications/specs/fitness-machine-service-1-0)
FTMS_REQUEST_CONTROL = 0x00
FTMS_CONTROL_POINT_UUID = 0X2AD9
FTMS_RESET = 0x01
FTMS_START_OR_RESUME = 0x07
FTMS_STOP_OR_PAUSE = 0x08

# ==== Incline Device Constants ====

# Incline Control's Custom Service and Characteristic (found from a BLE sniffer, not mentioned anywhere online)
INCLINE_CONTROL_SERVICE_UUID = "a026ee0b0a7d4ab397faf1500f9feb8b"
INCLINE_CONTROL_CHARACTERISTIC_UUID = "a026e0370a7d4ab397faf1500f9feb8b"

# Incline Control Op Values
INCLINE_REQUEST_CONTROL = 0x67
INCLINE_CONTROL_OP_CODE = 0x66
INCLINE_CONTROL_MAX_PART_1 = 0x6c # '0x666c07' is 19% incline
INCLINE_CONTROL_MAX_PART_2 = 0x07 
INCLINE_CONTROL_FLAT = 0x00 # '0x660000' is 0% incline
INCLINE_CONTROL_MIN_PART_1 = 0x19 # '0x6619fc' is -10% incline
INCLINE_CONTROL_MIN_PART_2 = 0xfc

# Climber MAC address
BIKE_01_KICKR_CLIMB_ADDRESS = "cf:5c:f0:0d:c7:68"

# BLE module adapter
BLE_ADAPTER = 'hci0'

# Helper constants
INCLINE_MIN = -10 # -10% incline down
INCLINE_FLAT = 0 # 0% incline flat
INCLINE_MAX = 19 # 19% incline up
INCLINE_CONTROL_INCREMENT_UNIT = 50 # the incline value is up or down by 50 unit each time
MIN_BYTE_VALUE = 0
MAX_BYTE_VALUE = 256

# ==== Resistance Device Constants ====
BIKE_01_KICKR_TRAINER_ADDRESS = "d9:07:e8:1c:db:94"
FTMS_SET_TARGET_RESISTANCE_LEVEL = 0x04
RESISTANCE_MIN = 0
RESISTANCE_MAX = 100 # 100% resistance

# ==== Wind Device Constants ====
BIKE_01_HEADWIND_ADDRESS = "ed:cb:f5:da:d3:f5"
# needs more research - not implemented