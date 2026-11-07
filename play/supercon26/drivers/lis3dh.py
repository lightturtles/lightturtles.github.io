"""LIS3DH accelerometer, for MicroPython.

A small driver from the Supercon 2026 "Badge Hacking for Beginners" workshop.
Every workshop driver works the same way:

    from lib.sao import i2c        # the badge's SAO I2C bus
    import lis3dh
    s = lis3dh.LIS3DH(i2c)
    s.reading()                    # (0.02, -0.01, 0.98): x, y, z in g
    s.text()                       # 'x 0.02  y -0.01  z 0.98 g'

How it works is in the "Read raw data" and "Raw bytes to real units" skills.
"""
import struct

ADDRESS = 0x19          # SparkFun's board; 0x18 with its address jumper closed

WHO_AM_I = 0x0F         # always reads 0x33 on a LIS3DH
CTRL_REG1 = 0x20        # how often to measure, and which axes
OUT_X_L = 0x28          # X, Y, Z: six bytes from here
AUTO_INCREMENT = 0x80   # add to a register number to read several in a row


class LIS3DH:
    units = "g"

    def __init__(self, i2c, address=ADDRESS):
        self.i2c = i2c
        self.address = address
        chip = self.i2c.readfrom_mem(address, WHO_AM_I, 1)[0]
        if chip != 0x33:
            raise RuntimeError("not a LIS3DH at {}: WHO_AM_I is {}".format(hex(address), hex(chip)))
        self.i2c.writeto_mem(address, CTRL_REG1, bytes([0x57]))   # 100 per second, X, Y and Z on

    def reading(self):
        """Acceleration as (x, y, z), in g. Lying still, the one pointing up reads about 1."""
        raw = self.i2c.readfrom_mem(self.address, OUT_X_L | AUTO_INCREMENT, 6)
        x, y, z = struct.unpack("<hhh", raw)     # low byte first, signed
        # 10-bit readings at the top of each 16; 4 thousandths of a g per step (±2 g range)
        return tuple((n >> 6) * 0.004 for n in (x, y, z))

    def text(self):
        """The reading as a short string, e.g. for the badge's screen."""
        return "x {:.2f}  y {:.2f}  z {:.2f} g".format(*self.reading())
