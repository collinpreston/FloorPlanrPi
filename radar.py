import datetime
import bluetooth
import serial

ser = serial.Serial("/dev/serial0", baudrate=230400)

try:

    # Set the socket type.
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

    # Get an available port on the Raspberry Pi.
    # port = bluetooth.get_available_port( bluetooth.RFCOMM )
    port = 1

    # Bind the socket server to the Raspberry Pi on the port we got above.
    server_sock.bind(("", port))

    # Now we will listen for connection on the port.
    server_sock.listen(1)

    # In order to allow for the phone to detect and identify the 
    # correct bluetooth connection, we need to advertise our service.
    UUID = "1e0ca4ea-299d-4335-93eb-27fcfe7fa848"
    bluetooth.advertise_service(server_sock, "FloorPlanr", UUID)

    # Now we can capture the details of the phone once the connection is
    # made.
    (client_sock, address) = server_sock.accept()

    print('Connected to ' + str(address))


    def sendLIDARData():
        distance_list = ""
        ser.write(b'b')

        while True:
            # Here we need to check to make sure that the phone
            # has not sent a stop command.
            # TODO: Check if the connection is still open and connected to the phone.
            # If not, then we need to keep the pi open and not crash.
            print('here')
            data = client_sock.recv(1024)


            if (data == 'Stop'):
                # If the phone sends a stop command, then we need
                # to break the loop and go back to listening for a start
                # command.
                break

            try:
                result = ser.read(42)
                if (result[-1] == result[-2]):
                    rpm = result[3] * 256 + result[2]
                    base_angle = (result[1] - 160) * 6
                    for x in range(6):
                        distance = result[((6 * (x + 1)) + 1)] * 256 + result[((6 * (x + 1)))]
                        distance_list = distance_list + "," + distance

                    # After collecting all 6 distances sent from each packet of 
                    # LIDAR data, we will send the distance data along with the
                    # base angle to the phone.
                    client_sock.send(datetime.datetime.now() + "_" + base_angle + ":" + distance_list + "#")
                break
            except IndexError:
                ser.write(b'e')
                print('Stopped! Out of sync.')
                # Here we will need to go back to the main while loop.
                # In the main loop we will check to see if we returned bacause of
                # the LIDAR being out of sync or it the phone sent a stop command.
                # We will return 1 to indicate an error.
                return 1
        # Here we return with 0 to indicate that the method did not throw any errors.
        # This means that we are returning because the phone sent a stop command.
        return 0


    lidar_execution_result = 0

    # Stay connected while waiting for instructions from the phone.
    while True:
        data = client_sock.recv(1024).decode()
        print(str(data))

        # If the sendLIDARData returned with an error, then we need
        # to call the method again.
        if (data == 'Start' or lidar_execution_result == 1):
            # Here we will call the function to start sending
            # LIDAR data to the phone.
            lidar_execution_result = sendLIDARData()

        # TODO: We need to monitor the bluetooth connection.  When the connection is
        # closed, we will need to reset the application (close the connection, 
        # go back to accepting connections).
except KeyboardInterrupt:
    ser.write(b'e')
    print('quit')
