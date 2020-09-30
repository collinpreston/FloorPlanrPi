#!/bin/bash
sudo hciconfig hci0 piscan 
sudo hciconfig hci0 sspmode 1
sleep 15
bluetoothctl -- discoverable on
bluetoothctl -- pairable on
bluetoothctl -- agent on
bluetoothctl -- default-agent
python3 /home/pi/Downloads/lighthouse/bluez-test-scripts/examples/simple-agent &
python3 /home/pi/Downloads/lighthouse/lighthouse.py

