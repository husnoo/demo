# https://github.com/waveshare/Pan-Tilt-HAT/blob/master/RaspberryPi/Servo_Driver/python/

import time
import math
import smbus2




class PCA9685:
    # Registers
    __MODE1              = 0x00
    __MODE2              = 0x01
    __PRESCALE           = 0xFE
    __LED0_ON_L          = 0x06
    __LED0_ON_H          = 0x07
    __LED0_OFF_L         = 0x08
    __LED0_OFF_H         = 0x09
    __MAX_VAL = 4096

    def __init__(self, address=0x40):
        self.bus = smbus2.SMBus(1)
        self.address = address
        self.write(self.__MODE1, 0x00)

    def write(self, reg, value):
        """ Writes an 8-bit value to the specified register/address """
        self.bus.write_byte_data(self.address, reg, value)

    def read(self, reg):
        """ Read an unsigned byte from the I2C device """
        result = self.bus.read_byte_data(self.address, reg)
        return result

    def setPWMFreq(self, freq):
        """ Sets the PWM frequency """
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        prescale = math.floor(prescaleval + 0.5)
        oldmode = self.read(self.__MODE1);
        newmode = (oldmode & 0x7F) | 0x10        # sleep
        self.write(self.__MODE1, newmode)        # go to sleep
        self.write(self.__PRESCALE, int(math.floor(prescale)))
        self.write(self.__MODE1, oldmode)
        time.sleep(0.005)
        self.write(self.__MODE1, oldmode | 0x80)
        self.write(self.__MODE2, 0x04)

    def setPWM(self, channel, on, off):
        """ Sets a single PWM channel """
        self.write(self.__LED0_ON_L+4*channel, on & 0xFF)
        self.write(self.__LED0_ON_H+4*channel, on >> 8)
        self.write(self.__LED0_OFF_L+4*channel, off & 0xFF)
        self.write(self.__LED0_OFF_H+4*channel, off >> 8)






