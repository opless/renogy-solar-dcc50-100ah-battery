import minimalmodbus
import json

class RenogyBattery(minimalmodbus.Instrument):
    def __init__(self, port_name, slave_address):
        minimalmodbus.Instrument.__init__(self, port_name, slave_address)
        self.serial.baudrate = 9600
        self.serial.timeout = 0.2

    CELL_VOLTAGE_BASE = 5000
    CELL_TEMP_BASE = 5017
    BMS_TEMP = 5035
    ENV_TEMP_BASE = 5037
    HEATER_TEMP_BASE = 5039
    CURRENT = 5042
    VOLTAGE = 5043
    REMAIN_CAPACITY = 5044
    MODULE_CAPACITY = 5046
    CYCLE_COUNT = 5048

    LIMIT_CHARGE_VOLTAGE = 5049
    LIMIT_DISCHARGE_VOLTAGE = 5050
    LIMIT_CHARGE_CURRENT = 5051
    LIMIT_DISCHARGE_CURRENT = 5052
    CELL_VOLTAGE_ALARM = 5100
    CELL_TEMPERATURE_ALARM = 5102
    OTHER_ALARMS = 5104
    STATUS_ONE = 5106
    STATUS_TWO = 5107
    STATUS_THREE = 5108
    CHARGE_DISCHARGE_STATUS = 5109
    SERIAL_NUMBER = 5110
    MANUFACTURER_VERSION = 5118
    MAIN_LINE_VERSION = 5119
    COMMUNICATION_PROTOCOL_VERSION = 5121
    BATTERY_NAME = 5122
    SOFTWARE_VERSION = 5130
    MANUFACTURER_NAME = 5132

    def get_array(self, reg_base, dp, signed=False):
        count = self.read_register(reg_base)
        elements = {}
        start = reg_base + 1
        for register in range(start, start + count):
            elements["cell_{}".format(register-start+1)] = (self.read_register(register, dp, signed=signed))
        return elements

    def cell_voltages(self):
        return self.get_array(self.CELL_VOLTAGE_BASE, 1)

    def cell_temperatures(self):
        return self.get_array(self.CELL_TEMP_BASE, 1, signed=True)

    def module_temperature(self):
        return self.read_register(self.BMS_TEMP, 1, signed=True)

# this throws an error.
#    def environment_temperatures(self):
#        return self.get_array(self.ENV_TEMP_BASE, 1)

    def heater_temperatures(self):
        return self.get_array(self.HEATER_TEMP_BASE, 1, signed=True)

    def module_current(self):
        return self.read_register(self.CURRENT, 2, signed=True)

    def module_voltage(self):
        return self.read_register(self.VOLTAGE, 1)

    def module_remaining_capacity(self):
        return float(self.read_long(self.REMAIN_CAPACITY)) / 1000.0

    def module_capacity(self):
        return float(self.read_long(self.MODULE_CAPACITY)) / 1000.0

    def module_cycle_count(self):
        return self.read_register(self.CYCLE_COUNT)

    def charge_voltage_limit(self):
        return self.read_register(self.LIMIT_CHARGE_VOLTAGE, 1, signed=True)

    def discharge_voltage_limit(self):
        return self.read_register(self.LIMIT_DISCHARGE_VOLTAGE, 1, signed=True)

    def charge_current_limit(self):
        return self.read_register(self.LIMIT_CHARGE_CURRENT, 2, signed=True)

    def discharge_current_limit(self):
        return self.read_register(self.LIMIT_DISCHARGE_CURRENT, 2, signed=True)

    @staticmethod
    def quad_bits(value):
        n = value & 3
        if n == 0:
            return "normal"
        elif n == 1:
            return "below_lower_limit"
        elif n == 2:
            return "above_upper_limit"
        else:  # n = 3
            return "other_alarm"

    def quad_bits_alarm(self, reg_base):
        value = self.read_long(reg_base)
        alarm_array = []
        for i in range(0, 16):
            alarm = self.quad_bits(value)
            value = value >> 2
            alarm_array.append(alarm)
        return alarm_array, value

    def quad_bits_for_names(self, reg_base, names):
        values, value = self.quad_bits_alarm(reg_base)
        ret_val = {}
        for i in range(0, len(names)):
            ret_val[names[i]] = values[i]

        keys = list(ret_val.keys())
        for i in keys:
            if i.startswith("reserved_"):
                ret_val.pop(i)
        ret_val["_value"] = value
        return ret_val

    def name_cells(self, is_v=True):
        names = []
        reg = self.CELL_VOLTAGE_BASE
        if not is_v:
            reg = self.CELL_TEMP_BASE
        count = self.read_register(reg)
        for i in range(0, count):
            names.append("cell_{}".format(i+1))
        return names

    def cell_voltage_alarm(self):
        prefixes = self.name_cells()
        return self.quad_bits_for_names(self.CELL_VOLTAGE_ALARM, prefixes)

    def cell_temperature_alarm(self):
        prefixes = self.name_cells(is_v=False)
        return self.quad_bits_for_names(self.CELL_TEMPERATURE_ALARM, prefixes)

    def other_alarm(self):
        prefixes = ["reserved_0", "reserved_1", "reserved_2", "reserved_3", "reserved_4", "reserved_5", "reserved_6",
                    "reserved_7", "reserved_8", "discharge_current", "charge_current", "heater_temperature_2",
                    "heater_temperature_1", "environment_temperature_2", "environment_temperature_1", "bms_temperature"]

        return self.quad_bits_for_names(self.OTHER_ALARMS, prefixes)

    def name_status_bits(self, reg, keys):
        value = self.read_register(reg)
        ret_val = {}
        for i in range(0, 16):
            result = (value & 1) > 0
            ret_val[keys[i]] = result
            value = value >> 1

        keys = list(ret_val.keys())
        for i in keys:
            if i.startswith("reserved_"):
                ret_val.pop(i)
        ret_val["_value"] = value
        return ret_val

    def status_one(self):
        statuses = ["short_circuit", "charge_mosfet", "discharge_mosfet", "using_module_power",
                    "charge_over_current_2", "discharge_over_current_2", "module_over_voltage", "cell_under_voltage",
                    "cell_over_voltage", "charge_over_current_1", "discharge_over_current_1", "discharge_under_temp",
                    "discharge_over_temp", "charge_under_temp", "charge_over_temp", "module_under_voltage"]
        return self.name_status_bits(self.STATUS_ONE, statuses)

    def status_two(self):
        statuses = ["cell_low_voltage", "cell_high_voltage", "module_low_voltage", "module_high_voltage",
                    "charge_low_temp", "charge_high_temp", "discharge_low_temp", "discharge_high_temp",
                    "buzzer_on", "reserved_9", "reserved_10", "fully_charged",
                    "reserved_12", "heater_on", "effective_discharge_current", "effective_charge_current"]

        return self.name_status_bits(self.STATUS_TWO, statuses)

    def status_three(self):
        statuses = ["cell_voltage_1_error", "cell_voltage_2_error", "cell_voltage_3_error", "cell_voltage_4_error",
                    "cell_voltage_5_error", "cell_voltage_6_error", "cell_voltage_7_error", "cell_voltage_8_error",
                    "cell_voltage_9_error", "cell_voltage_10_error", "cell_voltage_11_error", "cell_voltage_12_error",
                    "cell_voltage_13_error", "cell_voltage_14_error", "cell_voltage_15_error", "cell_voltage_16_error"]
        return self.name_status_bits(self.STATUS_THREE, statuses)

    def status_charge_discharge(self):
        statuses = ["reserved_0", "reserved_1", "reserved_2", "full_charge_request",
                    "charge_immediately_a", "charge_immediately_b", "discharge_enable", "charge_enable",
                    "reserved_8", "reserved_9", "reserved_10", "reserved_11",
                    "reserved_12", "reserved_13", "reserved_14", "reserved_15"]
        return self.name_status_bits(self.CHARGE_DISCHARGE_STATUS, statuses)

    def module_serial_number(self):
        return self.read_string(self.SERIAL_NUMBER, 8)

    def module_manufacture_version(self):
        return self.read_string(self.MANUFACTURER_VERSION, 1)  # possible error?

    def module_mainline_version(self):
        return self.read_string(self.MAIN_LINE_VERSION, 2)

    def bms_communication_protocol_version(self):
        return self.read_string(self.COMMUNICATION_PROTOCOL_VERSION, 1)

    def module_battery_name(self):
        return self.read_string(self.BATTERY_NAME, 8)

# throws an error
#    def module_manufacturer_name(self):
#        return self.read_string(self.MANUFACTURER_NAME)

    LIMIT_CELL_OVER_VOLTAGE = 5200
    LIMIT_CELL_HIGH_VOLTAGE = 5201
    LIMIT_CELL_LOW_VOLTAGE = 5202
    LIMIT_CELL_UNDER_VOLTAGE = 5203

    def cell_over_voltage(self):
        return self.read_register(self.LIMIT_CELL_OVER_VOLTAGE, 1)

    def cell_high_voltage(self):
        return self.read_register(self.LIMIT_CELL_HIGH_VOLTAGE, 1)

    def cell_low_voltage(self):
        return self.read_register(self.LIMIT_CELL_LOW_VOLTAGE, 1)

    def cell_under_voltage(self):
        return self.read_register(self.LIMIT_CELL_UNDER_VOLTAGE, 1)

    LIMIT_CELL_OVER_TEMPERATURE = 5204
    LIMIT_CELL_HIGH_TEMPERATURE = 5205
    LIMIT_CELL_LOW_TEMPERATURE = 5206
    LIMIT_CELL_UNDER_TEMPERATURE = 5207

    def cell_over_temperature(self):
        return self.read_register(self.LIMIT_CELL_OVER_TEMPERATURE, 1)

    def cell_high_temperature(self):
        return self.read_register(self.LIMIT_CELL_HIGH_TEMPERATURE, 1)

    def cell_low_temperature(self):
        return self.read_register(self.LIMIT_CELL_LOW_TEMPERATURE, 1)

    def cell_under_temperature(self):
        return self.read_register(self.LIMIT_CELL_UNDER_TEMPERATURE, 1)

    LIMIT_CHARGE_OVER_2 = 5208
    LIMIT_CHARGE_OVER_1 = 5209

    def charge_current_limit_1(self):
        return self.read_register(self.LIMIT_CHARGE_OVER_1, 2, signed=True)

    def charge_current_limit_2(self):
        return self.read_register(self.LIMIT_CHARGE_OVER_2, 2, signed=True)

    LIMIT_CHARGE_HIGH_CURRENT = 5210
    LIMIT_MODULE_OVER_VOLTAGE = 5211
    LIMIT_MODULE_HIGH_VOLTAGE = 5212
    LIMIT_MODULE_LOW_VOLTAGE = 5213
    LIMIT_MODULE_UNDER_VOLTAGE = 5214

    def charge_high_current_limit(self):
        return self.read_register(self.LIMIT_CHARGE_HIGH_CURRENT, 1)

    def module_over_voltage_limit(self):
        return self.read_register(self.LIMIT_MODULE_OVER_VOLTAGE, 1)

    def module_high_voltage_limit(self):
        return self.read_register(self.LIMIT_MODULE_HIGH_VOLTAGE, 1)

    def module_low_voltage_limit(self):
        return self.read_register(self.LIMIT_MODULE_LOW_VOLTAGE, 1)

    def module_under_voltage_limit(self):
        return self.read_register(self.LIMIT_MODULE_UNDER_VOLTAGE, 1)

    LIMIT_DISCHARGE_OVER_TEMPERATURE = 5215
    LIMIT_DISCHARGE_HIGH_TEMPERATURE = 5216
    LIMIT_DISCHARGE_LOW_TEMPERATURE = 5217
    LIMIT_DISCHARGE_UNDER_TEMPERATURE = 5218

    def discharge_over_temperature(self):
        return self.read_register(self.LIMIT_DISCHARGE_OVER_TEMPERATURE, 1, signed=True)

    def discharge_high_temperature(self):
        return self.read_register(self.LIMIT_DISCHARGE_HIGH_TEMPERATURE, 1, signed=True)

    def discharge_low_temperature(self):
        return self.read_register(self.LIMIT_DISCHARGE_LOW_TEMPERATURE, 1, signed=True)

    def discharge_under_temperature(self):
        return self.read_register(self.LIMIT_DISCHARGE_UNDER_TEMPERATURE, 1, signed=True)

    LIMIT_DISCHARGE_OVER2_CURRENT = 5219
    LIMIT_DISCHARGE_OVER1_CURRENT = 5220
    LIMIT_DISCHARGE_HIGH_CURRENT = 5221

    def discharge_over_current_1(self):
        return self.read_register(self.LIMIT_DISCHARGE_OVER1_CURRENT, 2, signed=True)

    def discharge_over_current_2(self):
        return self.read_register(self.LIMIT_DISCHARGE_OVER2_CURRENT, 2, signed=True)

    def discharge_high_current(self):
        return self.read_register(self.LIMIT_DISCHARGE_HIGH_CURRENT, 2, signed=True)

    def toJSON(self, indent=0):
        y = filter(lambda x: x.startswith("cell") or
                             x.startswith("bms") or
                             x.startswith("environment") or
                             x.startswith("heater") or
                             x.startswith("module") or
                             x.startswith("environment") or
                             x.startswith("charge") or
                             x.startswith("discharge") or
                             x.startswith("status") or
                             x.startswith("other"), dir(self))
        methods = list(y)
        d = {}
        for method in methods:
            m = getattr(self, method)
            d[method] = m()

        return json.dumps(d, indent=indent)
