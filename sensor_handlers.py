"""A set of singleton classes to handle sensor initialisation and utility to avoid conflict across subroutines"""
"""A new singleton class should be created for each new sensor and configured here so that it is consistant across the program"""
from abc import *
import warnings
import RPi.GPIO as GPIO
import logging
import time

""" 
!!! TO BE DONE !!! 
- decide and change the path for where we want logging files to be dumped
- probably organise for this module to be set on the PATH or something so it can be called any where (might be unnecessary and overkill)
- define sensor PINs in constants and import instead of defining in class
- decide on this module's name since it will be important ('sensors.py' is not an option)
- test it on the Pi
"""

# ======== Setup the GPIO ========

GPIO.setmode(GPIO.BOARD)

# ======== Initialise Sensor Logger ========

logger = logging.getLogger('sensor_output')
logger.setLevel(logging.DEBUG)

logger_formatter = logging.Formatter('%(asctime)s : %(message)s')

file_handler = logging.FileHandler('sensor_output.log')
file_handler.setFormatter(logger_formatter)

logger.addHandler(file_handler)

# ======== Abstract Sensor Basis Class ========

class Sensor(ABC,object):
    """Abstract Sensor Class to be basis of all sensor implementations"""

    _instance = None

    def __new__(cls,*args,**kwargs):
        """Initialise a single instance of the class if none exists, else return the already existing instance.\n
        Inspect _config method for parameters"""
        if cls._instance is None:
            cls._instance = super(Sensor, cls).__new__(cls)
            cls._instance._config(*args,**kwargs)
        return cls._instance
    
    @classmethod
    @abstractmethod
    def _config(self):
        """configure the sensor during initialisation"""
        pass
    
    @abstractmethod
    def state(self):
        """return the current sensor output"""
        pass

# ======== Sensor Class Implementations ========

class Button(Sensor):
    """Virtual Class to be used for all implimented buttons"""

    __PIN = None
    __NAME = None

    def _config(self,pin: int = __PIN):
        """Initialise the button on the GPIO"""

        # use passed pin if passed & warn using non-default pin is dangerous
        if not pin is self.__PIN: 
            warnings.warn('Setting the pin explicitly for {} should only be done for testing purposes and the current default pin {} should otherwise always be used implicitly or changed if needed.'.format(self.__NAME,self.__PIN))
            self.__PIN = pin
        
        # set the pin
        GPIO.setup(pin, GPIO.IN)
    
    def state(self) -> bool:
        """returns True/GPIO.HIGH if pressed\n
        returns False/GPIO.LOW if released"""

        # get the current state
        state = GPIO.input(self.__PIN)

        # publish to the logger
        logger.debug('{} : {}'.format(self.__NAME,state))

        # return the state
        return state

class R_Button(Button):

    __PIN = 11
    __NAME = 'RIGHT STEERING BUTTON'

class L_Button(Button):

    __PIN = 12
    __NAME = 'LEFT STEERING BUTTON'

# ======== Testing ========

if __name__ == "__main__":

    # ==== Steering Buttons Test ====
    # initialise the buttons
    right = R_Button()
    left = L_Button()

    # log their current states
    right.state()
    left.state()

    # delay to change state IRL for testing
    time.sleep(10)

    # reinitialising should not break anything and return the exact same objects
    right = R_Button()
    left = L_Button()

    # log the new states
    right.state()
    left.state()
    # ==== ===================== ====