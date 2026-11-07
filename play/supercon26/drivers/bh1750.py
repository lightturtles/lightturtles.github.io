"""BH1750 light sensor, for MicroPython.

A small driver from the Supercon 2026 "Badge Hacking for Beginners" workshop.
Every workshop driver works the same way:

    from lib.sao import i2c        # the badge's SAO I2C bus
    import bh1750
    s = bh1750.BH1750(i2c)
    s.reading()                    # 312.5: lux
    s.text()                       # '312 lux'

How it works is in the "Read raw data" and "Raw bytes to real units" skills.
"""
import time

ADDRESS = 0x23          # 0x5C if the board's ADDR pin is pulled high

POWER_ON = 0x01
CONTINUOUS_HIGH_RES = 0x10      # measure over and over, 1 lux steps, 120-180 ms each


class BH1750:
    units = "lux"

    def __init__(self, i2c, address=ADDRESS):
        self.i2c = i2c
        self.address = address
        self.i2c.writeto(address, bytes([POWER_ON]))
        self.i2c.writeto(address, bytes([CONTINUOUS_HIGH_RES]))
        self._started = time.ticks_ms()

    def reading(self):
        """The latest light level, in lux."""
        # The first measurement takes up to 180 ms. After that there's always one ready.
        wait = 180 - time.ticks_diff(time.ticks_ms(), self._started)
        if wait > 0:
            time.sleep_ms(wait)
        raw = self.i2c.readfrom(self.address, 2)
        return ((raw[0] << 8) | raw[1]) / 1.2   # high byte first; 1.2 counts per lux

    def text(self):
        """The reading as a short string, e.g. for the badge's screen."""
        return "{:.0f} lux".format(self.reading())
