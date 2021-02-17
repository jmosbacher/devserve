from datetime import datetime
from ctypes import (cdll,c_long, c_ulong, c_uint32,byref,
                     create_string_buffer,c_bool,c_char_p, 
                     c_int,c_int16,c_double, sizeof, c_voidp)

import time

import serial
import struct
import time
import threading
import logging
import numpy as np

from ...device import Device
from ._TLPM import TLPMWrapper


class TLPM(Device):
    public = [ 'resource_index', # connecting
        		'count', 'wavelength',                 # Device configuration
                'mode', 'autorange',      
                'power',    ] # Operations

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tlpm = TLPMWrapper()
        self._resource_index = kwargs.get("resource_index", 0)
        
    @property
    def resource_index(self):
        return self._resource_index

    @port.setter
    def resource_index(self, value):
        self._resource_index = value
        if self.connected:
            self.disconnect()
        self.connect()

    @property
    def power(self):
        if not self.connected:
            return
        power =  c_double()
        self._tlpm.measPower(byref(power))
        return power.value

    @property
    def count(self):
        pass

    @count.setter
    def count(self, value):
        pass

    @property
    def wavelength(self):
        pass

    @wavelength.setter
    def wavelength(self, value):
        pass

    @property
    def mode(self):
        pass

    @property
    def autorange(self):
        return self._tlpm.getCurrentAutoRange()


    @autorange.setter
    def autorange(self, value):
        if value in [0, False, 'False', 'false', 'off']:
            self._tlpm.setCurrentAutoRange(0)
        elif value in [1, True, 'True', 'true','on']:
            self._tlpm.setCurrentAutoRange(1)

    def connect(self):
        try:
            resourceName = create_string_buffer(1024)
            self._tlpm.getRsrcName(c_int(self.resource_index), resourceName)
            self._tlpm.open(resourceName, c_bool(True), c_bool(True))
        except Exception as e:
            logging.error(f"Exception raised while attempting to connect: {e}")

    def disconnect(self):
        self._tlpm.close()

    @property
    def connected(self):
        return self._tlpm.devSession > 0



