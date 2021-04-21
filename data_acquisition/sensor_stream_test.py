# ------------------------------------------------------------------------------------------------------------------
#   Sensor Stream App test program.
# ------------------------------------------------------------------------------------------------------------------
import time
import socket
import struct

# Socket configuration
UDP_IP = '192.168.1.104'
UDP_PORT = 8800
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.settimeout(0.001)

# Data acquisition loop
acc_data = []
gyro_data = []
mag_data = []

start_time = time.time()
update_time = 2
while True:

    try:
        # Read data from UDP connection
        data, addr = sock.recvfrom(1024*1024)

        # Decode binary stream.
        data_string = data.decode('ascii').split(",")

        # Append new sensor data
        time_stamp = float(data_string[0])
        nsensors = (len(data_string)-1)/4

        for ind in range(1, len(data_string), 4):
            type = int(data_string[ind])

            if type == 3:
                acc_data.append([time_stamp, float(data_string[ind+1]), float(data_string[ind+2]),
                                 float(data_string[ind+3])])
            elif type == 4:
                gyro_data.append([time_stamp, float(data_string[ind+1]), float(data_string[ind+2]),
                                  float(data_string[ind+3])])
            elif type == 5:
                mag_data.append([time_stamp, float(data_string[ind+1]), float(data_string[ind+2]),
                                 float(data_string[ind+3])])

    except socket.timeout:
        pass

    ellapsed_time = time.time() - start_time
    if ellapsed_time > update_time:

        start_time = time.time()

        # Print acceleration data
        print('Acceleration samples: ', len(acc_data))
        print('Sampling rate: ', len(acc_data)/ellapsed_time)
        print('Acceleration data: ', acc_data)

        # Print gyro data
        print('Gyro samples: ', len(gyro_data))
        print('Sampling rate: ', len(gyro_data)/ellapsed_time)
        print('Gyro data: ', gyro_data)

        # Print magetic data
        print('Magnetic samples: ', len(mag_data))
        print('Sampling rate: ', len(mag_data)/ellapsed_time)
        print('Magnetic data: ', mag_data)

        # Reset data buffers
        acc_data = []
        gyro_data = []
        mag_data = []
