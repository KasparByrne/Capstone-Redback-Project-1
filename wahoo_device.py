import gatt
from time import sleep
from constants import *
from ble_helper import *

# a sleep time to wait for a characteristic.writevalue() action to be completed
WRITEVALUE_WAIT_TIME = 0.5 # TODO: If this doesn't work well, it needs to change this short sleep mechainism to a async process mechainism for sending consequetive BLE commands (eg., threading control)


"""
TO DO:
    - switch out printing for logging
    - research & implement the wind device
"""

"""
So the WahooDevice class should handle setting up and connecting.
While the child classes should only handle controlling/reading the device.
"""

"""
If the tests do not pass try the following:
    For connection issues/with multiple devices:
    - Only instantiate the manager only once (outside of the class but still in this file)
    - Connect outside of the class like manager
    - Connect only once.

"""

class WahooDevice(gatt.Device):
    def __init__(self,mac_address: str):

        # connect to the BLE
        self.manager = gatt.DeviceManager(adapter_name=BLE_ADAPTER)
        super().__init__(mac_address,self.manager,True)

        # define the initial FTMS Service and the corresponding Characteristics
        self.ftms = [None] # store in a list so it is a reference
        self.ftms_control_point = None

        # define services to get characteristics of
        self.services_of_interest = [self.ftms]
    
    # Helper methods for logging request/connection error & success

    def connect_succeeded(self):
        super().connect_succeeded()
        print("[%s] Connected" % (self.mac_address))
    
    def connect_failed(self, error):
        super().connect_failed(error)
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))
        sys.exit()
    
    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print("[%s] Disconnected" % (self.mac_address))
    
    # These methods handle the ftms connection

    def set_service_or_characteristic(self, service_or_characteristic):
        """Identify and store the service/characteristic"""

        # identify the FTMS service
        if service_or_characteristic_found(FTMS_UUID, service_or_characteristic.uuid):
            self.ftms[0] = service_or_characteristic
        
        # identify the FTMS control point characteristic
        elif service_or_characteristic_found(FTMS_CONTROL_POINT_UUID, service_or_characteristic.uuid):
            self.ftms_control_point = service_or_characteristic

    def ftms_request_control(self):
        """Request control of the FTMS control point enabling us to execute functions on the FTMS server"""
        if self.ftms_control_point:
            # request FTMS control
            print("Requesting FTMS control...")
            self.ftms_control_point.write_value(bytearray([FTMS_REQUEST_CONTROL]))
            sleep(WRITEVALUE_WAIT_TIME)
    
    def ftms_reset_settings(self):
        """Reset control of the FTMS control point and features"""
        print("Initiating to reset control settings...")
        if self.ftms_control_point:
            # reset FTMS control settings
            print("Resetting FTMS control settings...")
            self.ftms_control_point.write_value(bytearray([FTMS_RESET]))
            sleep(WRITEVALUE_WAIT_TIME)
    
    # this is the main process that will be run all time after manager.run() is called
    def services_resolved(self):
        """This is an override of the GATT.service_resolve() method which is automatically run when manager.run() is ran"""
        super().services_resolved()

        print("[%s] Resolved services" % (self.mac_address))
        for service in self.services:
            print("[%s]\tService [%s]" % (self.mac_address, service.uuid))
            self.set_service_or_characteristic(service)

            for characteristic in service.characteristics:
                print("[%s]\t\tCharacteristic [%s]" % (self.mac_address, characteristic.uuid))
                print("The characteristic value is: ", characteristic.read_value())

                for soi in self.services_of_interest:
                    if soi[0] == service:
                        self.set_service_or_characteristic(characteristic)

        # continue if FTMS service is found from the BLE device
        if self.ftms:
            # reset control settings while initiating the BLE connection
            self.ftms_reset_settings()

class InclineDevice(WahooDevice):

    def __init__(self):
        super().__init__(BIKE_01_KICKR_CLIMB_ADDRESS)

        # define the initial Incline Service and the corresponding Characteristics
        self.custom_incline_service = [None]
        self.custom_incline_characteristic = None

        # add the custom incline service as a SOI
        self.services_of_interest.append(self.custom_incline_service)

        # define the initial inclination values
        self.inclination = 0
        self.new_inclination = None

        # start the device connection and process
        self.manager.run()
        self.connect()

    def set_service_or_characteristic(self, service_or_characteristic):
        super().set_service_or_characteristic(service_or_characteristic)

        # identify the incline control custom service
        if service_or_characteristic_found_full_match(INCLINE_CONTROL_SERVICE_UUID, service_or_characteristic.uuid):
            self.custom_incline_service[0] = service_or_characteristic
        
        # identify the incline custom control point characteristic
        elif service_or_characteristic_found_full_match(INCLINE_CONTROL_CHARACTERISTIC_UUID, service_or_characteristic.uuid):
            self.custom_incline_characteristic = service_or_characteristic
    
    def ftms_reset_settings(self):

        if self.ftms_control_point:

            # reset normally
            super().ftms_reset_settings()

            # request incline control
            self.custom_control_point_enable_notifications()

            # reset incline to the flat level: 0%
            self.inclination = 0
            self.custom_control_point_set_target_inclination(self.inclination)
    
    def custom_control_point_enable_notifications(self):
        """We need to subscribe to be notified if our GATT feature call was successful"""

        if self.custom_incline_characteristic:
            # has to do this step to be able to send incline value successfully
            print("Enabling notifications for custom incline endpoint...")
            self.custom_incline_characteristic.enable_notifications()
            sleep(WRITEVALUE_WAIT_TIME)
    
    # the inclination value range is -10 to 19, in Percent with a resolution of 0.5%
    def custom_control_point_set_target_inclination(self, new_inclination):
        """Calls feature to set a new absolute inclination value"""
        print(f"Trying to set a new inclination value: {new_inclination}")

        if self.custom_incline_characteristic:
            # send the new inclination value to the custom characteristic
            print("values are: ", convert_incline_to_op_value(new_inclination))
            self.custom_incline_characteristic.write_value(bytearray([INCLINE_CONTROL_OP_CODE] + convert_incline_to_op_value(new_inclination)))
            self.new_inclination = new_inclination
            sleep(WRITEVALUE_WAIT_TIME)

class BikeDevice(WahooDevice):
    """Resistance & Candence, control & data"""
    def __init__(self):
        super().__init__(BIKE_01_KICKR_TRAINER_ADDRESS)

        # define the initial resistance values
        self.resistance = 0
        self.new_resistance = None

        # define the Characteristics for Indoor Bike Data (reporting speed, cadence and power)
        self.indoor_bike_data = None
    
    def set_service_or_characteristic(self, service_or_characteristic):
        super().set_service_or_characteristic(service_or_characteristic)

        # identify the indoor bike characteristic
        if service_or_characteristic_found(INDOOR_BIKE_DATA_UUID, service_or_characteristic.uuid):
            self.indoor_bike_data = service_or_characteristic
    
    def ftms_reset_settings(self):
        if self.ftms_control_point:
            # enable notifications for Indoor Bike Data
            self.indoor_bike_data.enable_notifications()

            # reset normally
            super().ftms_reset_settings()

            # reset resistance down to 0%
            self.resistance = 0
            self.ftms_set_target_resistance_level(self.resistance)

    # process the Indoor Bike Data
    # The KICKR Trainer only reports instantaneous speed, cadence and power
    def process_indoor_bike_data(self, value):
        """Read speed, candence & power values from binary attribute flag"""
        flag_instantaneous_speed = not((value[0] & 1) >> 0)
        flag_instantaneous_cadence = (value[0] & 4) >> 2
        flag_instantaneous_power = (value[0] & 64) >> 6
        offset = 2

        if flag_instantaneous_speed:
            self.instantaneous_speed = float((value[offset+1] << 8) + value[offset]) / 100.0 * 5.0 / 18.0
            offset += 2
            print(f"Instantaneous Speed: {self.instantaneous_speed} m/s")

        if flag_instantaneous_cadence:
            self.instantaneous_cadence = float((value[offset+1] << 8) + value[offset]) / 10.0
            offset += 2
            print(f"Instantaneous Cadence: {self.instantaneous_cadence} rpm")

        if flag_instantaneous_power:
            self.instantaneous_power = int((value[offset+1] << 8) + value[offset])
            offset += 2
            print(f"Instantaneous Power: {self.instantaneous_power} W")

        if offset != len(value):
            print("ERROR: Payload was not parsed correctly")
            return
    
    # the resistance value is UINT8 type and unitless with a resolution of 0.1
    def ftms_set_target_resistance_level(self, new_resistance):
        """Write a new resistance level to the bike"""
        print(f"Trying to set a new resistance value: {new_resistance}")

        if self.ftms_control_point:
            # initiate the action
            self.ftms_control_point.write_value(bytearray([FTMS_SET_TARGET_RESISTANCE_LEVEL, new_resistance]))
            self.new_resistance = new_resistance
            sleep(WRITEVALUE_WAIT_TIME)
        

class WindDevice(WahooDevice):
    def __init__(self):
        super().__init__(BIKE_01_HEADWIND_ADDRESS)
        """Not really implemented - Needs more research"""
        pass