import minimalmodbus
import json


class RenogyDCC50S(minimalmodbus.Instrument):
    def __init__(self, portname, slaveaddress):
        minimalmodbus.Instrument.__init__(self, portname, slaveaddress)

    RATED_VOLTAGE_CURRENT = 0xA
    PRODUCT_MODEL = 0x0C
    VERSION_SOFTWARE = 0x14
    VERSION_HARDWARE = 0x16
    SERIAL_NUMBER = 0x18

    def product_configuration(self):
        reg = self.read_register(self.RATED_VOLTAGE_CURRENT)
        v = reg >> 8
        a = reg & 0xFF
        return {"volts": v, "amps": a}

    def product_model(self):
        text = self.read_string(self.PRODUCT_MODEL, 8)
        return text

    def product_software_version(self):
        num = self.read_long(self.VERSION_SOFTWARE)
        major = num >> 16
        minor = (num >> 8) & 0xFF
        build = num & 0xFF
        return "{}.{}.{}".format(major, minor, build)

    def product_hardware_version(self):
        num = self.read_long(self.VERSION_HARDWARE)
        major = num >> 16
        minor = (num >> 8) & 0xFF
        build = num & 0xFF
        return "{}.{}.{}".format(major, minor, build)

    def product_serial_number(self):
        num = self.read_long(self.SERIAL_NUMBER)
        return "{:08x}".format(num)

    BATT_SOC = 0x100
    BATT_VOLTAGE = 0x101
    CHARGE_MAX_CURRENT = 0x102
    TEMP_INT_EXT = 0x103
    ALTERNATOR_VOLTAGE = 0x104
    ALTERNATOR_CURRENT = 0x105
    ALTERNATOR_POWER = 0x106
    SOLAR_VOLTAGE = 0x107
    SOLAR_CURRENT = 0x108
    SOLAR_POWER = 0x109
    CHARGE_STATE1 = 0x120
    ALARM_A = 0x121
    ALARM_B = 0x122
    BATT_MAX_CHARGE_CURRENT = 0xE001
    BATT_NOMINAL_CAPACITY = 0xE002
    BATT_TYPE = 0xE004

    def battery_state_of_charge(self):
        # percent
        num = self.read_register(self.BATT_SOC)
        return num

    def battery_voltage(self):
        return self.read_register(self.BATT_VOLTAGE, 1)

    def battery_max_charge_current(self):
        return self.read_register(self.BATT_MAX_CHARGE_CURRENT, 2)

    def battery_nominal_capacity(self):
        return self.read_register(self.BATT_NOMINAL_CAPACITY)

    def battery_type(self):
        num = self.read_register(self.BATT_TYPE)
        if num == 0:
            return "UserDefined"
        elif num == 1:
            return "OpenCell"
        elif num == 2:
            return "Sealed"
        elif num == 3:
            return "Gel"
        elif num == 4:
            return "LiFePO4"
        else:
            return "Unknown#{}".format(num)

    def temperature_probes(self):
        num = self.read_register(self.TEMP_INT_EXT)
        lo = num & 0xFF
        hi = num >> 8

        los = int.from_bytes(lo.to_bytes(1, "big"), "big", signed=True)
        his = int.from_bytes(hi.to_bytes(1, "big"), "big", signed=True)

        return {"internal": his, "probe": los}

    def voltage_alternator(self):
        return self.read_register(self.ALTERNATOR_VOLTAGE, 1)

    def current_alternator(self):
        return self.read_register(self.ALTERNATOR_CURRENT, 2, signed=True)

    def power_alternator(self):
        return self.read_register(self.ALTERNATOR_POWER, signed=True)

    def voltage_solar(self):
        return self.read_register(self.SOLAR_VOLTAGE, 1)

    def current_solar(self):
        return self.read_register(self.SOLAR_CURRENT, 2, signed=True)

    def power_solar(self):
        return self.read_register(self.SOLAR_POWER, signed=True)

    def name_status_bits(self, reg, keys):
        value = self.read_register(reg)
        ret_val = {}
        for i in range(0, len(keys)):
            result = (value & 1) > 0
            ret_val[keys[i]] = result
            value = value >> 1

        keys = list(ret_val.keys())
        for i in keys:
            if i.startswith("reserved#"):
                ret_val.pop(i)
        ret_val["_value"] = value
        return ret_val

    def charge_state(self):
        status = ["no_charging", "reserved#2", "mppt_charging", "equalization",
                  "boost", "float", "current_limited", "reserved#8",
                  "direct"]
        ret = self.name_status_bits(self.CHARGE_STATE1, status)
        return ret

    def alarm_a(self):
        status = ["reserved#1", "reserved#2", "reserved#3", "reserved#4",
                  "controller_inside_over_temp", "alternator_input_over_current", "reserved#7", "reserved#8",
                  "alternator_input_over_voltage_protection", "starter_battery_reverse_polarity",
                  "bms_over_charge_protection", "low_temperature_cutoff"]
        return self.name_status_bits(self.ALARM_A, status)

    def alarm_b(self):
        status = ["battery_over_discharged", "battery_over_charged", "battery_under_voltage_warning", "reserved#4",
                  "reserved#5", "controller_inside_temp_too_high", "battery_over_temp", "solar_input_too_high",
                  "reserved#9", "solar_input_over_voltage", "reserved#11", "reserved#12",
                  "solar_reverse_polarity"]
        return self.name_status_bits(self.ALARM_B, status)

    def toJSON(self, indent=0):
        y = filter(lambda x: x.startswith("battery") or
                             x.startswith("temperature") or
                             x.startswith("voltage") or
                             x.startswith("current") or
                             x.startswith("power") or
                             x.startswith("charge") or
                             x.startswith("product") or
                             x.startswith("alarm"), dir(self))
        methods = list(y)
        d = {}
        for method in methods:
            m = getattr(self, method)
            d[method] = m()

        return json.dumps(d, indent=indent)
