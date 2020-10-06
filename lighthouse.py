import bluetooth
import serial
import logging

ser = serial.Serial("/dev/serial0", baudrate=230400)

try:

    # Set the socket type.
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    port = 1

    # Bind the socket server to the Raspberry Pi on the port we got above.
    server_sock.bind(("", port))

    # Now we will listen for connection on the port.
    server_sock.listen(1)

    # In order to allow for the phone to detect and identify the
    # correct bluetooth connection, we need to advertise our service.
    UUID = "1e0ca4ea-299d-4335-93eb-27fcfe7fa848"
    bluetooth.advertise_service(server_sock, "raspberrypi", UUID)

    (client_sock, address) = server_sock.accept()
    client_sock.setblocking(False)

    ser.write(b'e')

    print("Awaiting connection...")


    def sendLIDARData(dataPacketSize):

        #print("Starting LiDAR")
        ser.write(b'b')
        while True:
            try:
                #print("reading from bluetooth...")
                data = client_sock.recv(1024).decode()
                #print("read from bluetooth...")
            except bluetooth.btcommon.BluetoothError:
                data = ""
                #print("Nothing to read.")

            if data == 'stop':
                # If the phone sends a stop command, then we need
                # to break the loop and go back to listening for a start
                # command.
                #print("stop command received!")
                ser.write(b'e')
                break

            try:
                ser.reset_input_buffer()
                #print("reading data from LiDAR...")
                result = ser.read(dataPacketSize)
                #print("read data from LiDAR.")

                #print("sending data to bluetooth...")
                client_sock.send(result)
                #print("sent data to bluetooth")

            except IndexError:
                #print('IndexError')
                ser.write(b'e')
                # Here we will need to go back to the main while loop.
                # In the main loop we will check to see if we returned because of
                # the LIDAR being out of sync or it the phone sent a stop command.
                # We will return 1 to indicate an error.
                return 1
            except bluetooth.btcommon.BluetoothError as e:
                print(e.errno)
                if (type(e).__name__ == "[Errno 104] Connection reset by peer)"):
                    # print('Bluetooth disconnected or connection lost...')
                    ser.write(b'e')
                    return 2
        return 0

    lidar_execution_result = 0

    # Stay connected while waiting for instructions from the phone.
    while True:
        try:
            #print("reading from bluetooth...")
            data = client_sock.recv(1024).decode()
            #print("read from bluetooth.")
        except bluetooth.btcommon.BluetoothError:
            data = ""
            #print("Nothing to read.")

        # If the sendLIDARData returned with an error, then we need
        # to call the method again.
        if data[:5] == 'start' or lidar_execution_result == 1:
            # Here we will call the function to start sending
            # LIDAR data to the phone.
            lidar_execution_result = sendLIDARData(int(data[5:]))

        if lidar_execution_result == 2:
            #print("waiting for bluetooth device to connect...")
            (client_sock, address) = server_sock.accept()
            client_sock.setblocking(False)
            lidar_execution_result = 0
except KeyboardInterrupt:
    ser.write(b'e')
