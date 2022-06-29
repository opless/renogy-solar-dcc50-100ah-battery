# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import minimalmodbus

import battery

# for device in range(1,256):
#    serial_port = "/dev/tty.usbserial-A95HK35A"
#    print("Attempting Device:", device)
#    bat = battery.RenogyBattery(serial_port, device)
#    try:
#        print("name:", bat.battery_name())
#    except minimalmodbus.NoResponseError:
#        pass
serial_port = "/dev/tty.usbserial-A95HK35A"
device = 247
bat = battery.RenogyBattery(serial_port, device)

print(bat.toJSON(4))

#print(bat.discharge_over_current_1())
#print(bat.discharge_over_current_2())
print("remaining capacity:", bat.module_remaining_capacity())