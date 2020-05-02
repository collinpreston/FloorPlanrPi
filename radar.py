import serial
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np

ser = serial.Serial ("/dev/serial0", baudrate=230400)

def init():
    r = np.arange(1, 361, 1)
    theta = np.radians(r)
    fig = plt.figure()
    ax = fig.add_subplot(111, polar=True)
    distance_list = [None] * 360
    total = 0

    while True:
        try:
            result = ser.read(42)  
            if (result[-1] == result[-2]):
                rpm = result[3]*256 + result[2]
                #print("RPM" + str(rpm))
                base_angle = (result[1] - 160)*6
                for x in range(6):
                    angle = base_angle + x
                    distance = result[((6*(x+1))+1)]*256 + result[((6*(x+1)))]
                    if distance_list[angle] != distance:
                        if distance > 0:
                           distance_list[angle] = distance
                           total += 1
                        else:
                            distance_list[angle] = 4200
                            total += 1
            print(total)
            if total >= 360:
                total = 0
                plt.cla()
                ax.plot(theta, distance_list)
                plt.pause(.1)
                        
        except IndexError:
            ser.write(b'e')
            print('Stopped! Out of sync.')
        
try:
    ser.write(b'b')
    init()
    plt.show()
    

except KeyboardInterrupt:
    ser.write(b'e')
    print('Stop')

