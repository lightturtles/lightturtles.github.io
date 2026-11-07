"""AHT20 temperature and humidity sensor, for MicroPython.

A small driver from the Supercon 2026 "Badge Hacking for Beginners" workshop.
Every workshop driver works the same way:

    from lib.sao import i2c        # the badge's SAO I2C bus
    import aht20
    s = aht20.AHT20(i2c)
    s.reading()                    # (22.4, 41.0): °C and %RH
    s.text()                       # '22.4 °C  41 %RH'

How it works is in the "Read raw data" and "Raw bytes to real units" skills.
"""
import time

ADDRESS = 0x38


class AHT20:
    units = ("°C", "%RH")

    def __init__(self, i2c, address=ADDRESS):
        self.i2c = i2c
        self.address = address
        time.sleep_ms(40)                        # the chip needs 40 ms after power-up
        if not self._status() & 0x08:            # bit 3: calibrated and ready
            self.i2c.writeto(address, bytes([0xBE, 0x08, 0x00]))   # "initialize"
            time.sleep_ms(10)

    def _status(self):
        return self.i2c.readfrom(self.address, 1)[0]

    def reading(self):
        """Measure now. Returns (temperature in °C, relative humidity in %). Takes about 80 ms."""
        self.i2c.writeto(self.address, bytes([0xAC, 0x33, 0x00]))   # "measure"
        time.sleep_ms(80)
        raw = self.i2c.readfrom(self.address, 6)
        while raw[0] & 0x80:                     # bit 7: still measuring
            time.sleep_ms(10)
            raw = self.i2c.readfrom(self.address, 6)
        # Two 20-bit numbers, packed into bytes 1-5. Byte 3 is split between them.
        hum = (raw[1] << 12) | (raw[2] << 4) | (raw[3] >> 4)
        temp = ((raw[3] & 0x0F) << 16) | (raw[4] << 8) | raw[5]
        return temp * 200 / 2**20 - 50, hum * 100 / 2**20

    def text(self):
        """The reading as a short string, e.g. for the badge's screen."""
        t, h = self.reading()
        return "{:.1f} °C  {:.0f} %RH".format(t, h)
