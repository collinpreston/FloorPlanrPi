import bluetooth
import serial
import time

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

    ser.write(b'e')

    def sendLIDARData(dataPacketSize):

        while True:
            ser.reset_input_buffer()
            # Here we need to check to make sure that the phone
            # has not sent a stop command.
            print("waiting to receive")
            #data = client_sock.recv(1024).decode()

            if data == 'stop':
                # If the phone sends a stop command, then we need
                # to break the loop and go back to listening for a start
                # command.
                break

            ser.write(b'b')
            while True:
                try:
                    result = ser.read(dataPacketSize)
                    ser.reset_input_buffer()
                    client_sock.send(result)

                except IndexError:
                    print('IndexError')
                    ser.write(b'e')
                    # Here we will need to go back to the main while loop.
                    # In the main loop we will check to see if we returned because of
                    # the LIDAR being out of sync or it the phone sent a stop command.
                    # We will return 1 to indicate an error.
                    return 1
                except bluetooth.btcommon.BluetoothError:
                    print('Bluetooth disconnected or connection lost')
                    ser.write(b'e')
                    return 2

        # Here we return with 0 to indicate that the method did not throw any errors.
        # This means that we are returning because the phone sent a stop command.
        return 0

    lidar_execution_result = 0

    # Stay connected while waiting for instructions from the phone.
    while True:
        data = client_sock.recv(1024).decode()

        # If the sendLIDARData returned with an error, then we need
        # to call the method again.
        if data[:5] == 'start' or lidar_execution_result == 1:
            # Here we will call the function to start sending
            # LIDAR data to the phone.
            lidar_execution_result = sendLIDARData(int(data[5:]))

        if lidar_execution_result == 2:
            (client_sock, address) = server_sock.accept()
            lidar_execution_result = 0
except KeyboardInterrupt:
    ser.write(b'e')

