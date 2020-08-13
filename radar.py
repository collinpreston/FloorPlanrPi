import bluetooth
import serial
import datetime
import time

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

        while True:
            # TODO: Put a pause after the read.
            ser.reset_input_buffer()
            ser.write(b'b')
            # Here we need to check to make sure that the phone
            # has not sent a stop command.
            #data = client_sock.recv(1024).decode()
            unique_values = 0
            supreme_list = ""
            distance_list = ""

            if data == 'Stop':
                # If the phone sends a stop command, then we need
                # to break the loop and go back to listening for a start
                # command.
                print('Stop')
                break

            total_result = []
            collected_data = 0
            while collected_data < 180:
                try:
                    total_result += ser.read(42)
                    collected_data += 1

                except IndexError:
                    ser.write(b'e')
                    print('Stopped! Out of sync.')
                    # Here we will need to go back to the main while loop.
                    # In the main loop we will check to see if we returned bacause of
                    # the LIDAR being out of sync or it the phone sent a stop command.
                    # We will return 1 to indicate an error.
                    return 1

            data_group = 0
            while unique_values < 180:
                result = total_result[(data_group * 42):(42 * data_group) + 42]
                # TODO: there is the chance that we don't enter the if loop and thus get
                # stuck in this while loop.  We should have an else condition.
                print(str(result[-1]) + " " + str(result[-2]))
                if result[-1] == result[-2]:
                    data_group += 1
                    base_angle = (result[1] - 160) * 6
                    for x in range(6):
                        distance = result[((6 * (x + 1)) + 1)] * 256 + result[(6 * (x + 1))]
                        distance_list = str(distance_list) + "," + str(distance)
                        unique_values += 1
                    supreme_list += str(datetime.datetime.now()) + "_" + str(base_angle) + "*" + str(
                        distance_list) + "#"

                    distance_list = ""
            # After collecting all 6 distances sent from each packet of
            # LIDAR data, we will send the distance data along with the
            # base angle to the phone.
            client_sock.send(supreme_list)
            print(str(datetime.datetime.now()))
            ser.write(b'e')

            # We need to sleep after sending the stop command to the lidar.  Otherwise the lidar will not turn
            # back on.
            time.sleep(.005)

        # Here we return with 0 to indicate that the method did not throw any errors.
        # This means that we are returning because the phone sent a stop command.
        return 0


    lidar_execution_result = 0

    # Stay connected while waiting for instructions from the phone.
    while True:
        data = client_sock.recv(1024).decode()
        print(data)

        # If the sendLIDARData returned with an error, then we need
        # to call the method again.
        if data == 'Start' or lidar_execution_result == 1:
            # Here we will call the function to start sending
            # LIDAR data to the phone.
            lidar_execution_result = sendLIDARData()

        # TODO: We need to monitor the bluetooth connection.  When the connection is
        # closed, we will need to reset the application (close the connection,
        # go back to accepting connections).
except KeyboardInterrupt:
    ser.write(b'e')
    print('quit')
