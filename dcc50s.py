import minimalmodbus


class RenogyDCC50S(minimalmodbus.instrument):
    def __init__(self, portname, slaveaddress):
        minimalmodbus.instrument.__init__(self, portname, slaveaddress)

    RATED_VOLTAGE_CURRENT = 0xA
    PRODUCT_MODEL = 0x0C

    def rated_voltage_current(self):
        reg = self.read_register(self.RATED_VOLTAGE_CURRENT)
        v = reg >> 8
        a = reg & 0xFF
        return (v, a)

    def product_model(self):
        str = self.read_string(self.PRODUCT_MODEL, 8)
        return str

    def software_version(self):
        num = self.read_long(self.VERSION_SOFTWARE)
        major = num >> 16
        minor = (num >> 8) & 0xFF
        build = num & 0xFF
        return "{}.{},{}".format(major, minor, build)

    def hardware_version(self):
        num = self.read_long(self.VERSION_HARDWARE)
        major = num >> 16
        minor = (num >> 8) & 0xFF
        build = num & 0xFF
        return "{}.{},{}".format(major, minor, build)

    def product_serial_number(self):
        num = self.read_long(self.SERIAL_NUMBER)
        return "{:08x}".format(num)
