"""CAP1203 capacitive touch slider (SparkFun SEN-15344), for MicroPython.

A small driver from the Supercon 2026 "Badge Hacking for Beginners" workshop.
Every workshop driver works the same way:

    from lib.sao import i2c        # the badge's SAO I2C bus
    import cap1203
    s = cap1203.CAP1203(i2c)
    s.reading()                    # 63.0: finger position, 0 (left) to 100 (right); None if no touch
    s.text()                       # 'touch at 63 %'
    s.touched()                    # (False, True, True): left, middle, right pads

How it works is in the "Read raw data" and "Raw bytes to real units" skills.
"""
import struct

ADDRESS = 0x28          # fixed in the chip

MAIN_CONTROL = 0x00     # write 0 to clear the remembered touches
INPUT_STATUS = 0x03     # bit 0 left, bit 1 middle, bit 2 right
DELTA_COUNT = 0x10      # 0x10-0x12: how far each pad has moved from normal (signed)
PRODUCT_ID = 0xFD       # always reads 0x6D on a CAP1203


class CAP1203:
    units = "%"

    def __init__(self, i2c, address=ADDRESS, threshold=20):
        self.i2c = i2c
        self.address = address
        self.threshold = threshold      # total delta count below this = nobody touching
        chip = self.i2c.readfrom_mem(address, PRODUCT_ID, 1)[0]
        if chip != 0x6D:
            raise RuntimeError("not a CAP1203 at {}: product ID is {}".format(hex(address), hex(chip)))

    def touched(self):
        """Which pads were touched since the last call: (left, middle, right)."""
        status = self.i2c.readfrom_mem(self.address, INPUT_STATUS, 1)[0]
        self.i2c.writeto_mem(self.address, MAIN_CONTROL, bytes([0]))   # forget them
        return bool(status & 1), bool(status & 2), bool(status & 4)

    def reading(self):
        """Finger position along the slider, 0 (left) to 100 (right), or None if no touch."""
        deltas = struct.unpack("bbb", self.i2c.readfrom_mem(self.address, DELTA_COUNT, 3))
        left, mid, right = (max(n, 0) for n in deltas)
        total = left + mid + right
        if total < self.threshold:
            return None
        # Weight each pad by where it sits: left 0 %, middle 50 %, right 100 %.
        return (mid * 50 + right * 100) / total

    def text(self):
        """The reading as a short string, e.g. for the badge's screen."""
        pos = self.reading()
        return "no touch" if pos is None else "touch at {:.0f} %".format(pos)
