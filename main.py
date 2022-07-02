# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import minimalmodbus

import battery
import dcc50s

#for device in range(90,99):
#    serial_port = "/dev/tty.usbserial-A95HK35A"
#    print("Attempting Device:", device)
#    dcc = dcc50s.RenogyDCC50S(serial_port, device)
#    bat = battery.RenogyBattery(serial_port, device)
#    try:
#        print("type:", dcc.battery_voltage())
#        print("name:", bat.module_battery_name())
#    except minimalmodbus.NoResponseError:
#        pass
serial_port = "/dev/tty.usbserial-A95HK35A"
#device = 247
#device = 2
#bat = battery.RenogyBattery(serial_port, device)

#print(bat.toJSON(4))

#print(bat.discharge_over_current_1())
#print(bat.discharge_over_current_2())
#print("remaining capacity:", bat.module_remaining_capacity())

device = 48

bat = battery.RenogyBattery(serial_port, device)
print(bat.toJSON(4))

device = 97
dcc = dcc50s.RenogyDCC50S(serial_port, device)
print(dcc.toJSON(4))

#battery on 48
#dcdc on 97