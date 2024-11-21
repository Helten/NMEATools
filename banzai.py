from multiprocessing import Process, Pipe
from multiprocessing.connection import Connection
import socket
import time
from pathlib import Path
import argparse
import serial
import time


def tcp(pipeConn: Connection, port: int):
    print("tcp!")
    print(pipeConn)
    HOST = '127.0.0.1'  # Localhost
    #PORT = 65432

    # Create a socket object
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, port))
        s.listen(1)
        print(f'Server listening on {HOST}:{port}')
        
        # Wait for a connection
        tcpConn, addr = s.accept()
        with tcpConn:            
            print(f'Connected by {addr}')            
            while True:
                data = pipeConn.recv()
                if not data:
                    break
                #print(f'data={data}')        
                tcpConn.sendall(data)    


def bt(pipeConn: Connection, port: str):
    print('bt!')
    #print(pipeConn)


    ser = serial.Serial(port, 9600, timeout=15)
    print("connected to bt")
    time.sleep(2) 

    ser.write(b'Hello HC-06')  # Send data to HC-06
    while True:
        sentence = ser.readline().decode('utf-8').rstrip()
        if not sentence:
            break;
        data = bytes(sentence + "\r\n", 'utf-8')
        ser.write(data)

    # ser.close()
    # with open(r"TrimbleR1_20160310-165531.txt", 'r') as file:
    #     sentences = [bytes(l.rstrip()  + '\r\n', 'utf-8') for l in file.readlines()]
    # while True:
    #     data = sentences.pop(0)
    #     sentences.append(data)    
    #     pipeConn.send(data)  
    #     time.sleep(1)
  
  
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Send NMEA data from Bluetooth to TCP.')
    parser.add_argument("tcpPort")
    parser.add_argument("comPort")
    args = parser.parse_args()
    tcpPort = int(args.tcpPort)
    comPort = args.comPort

    pipe1, pipe2 = Pipe()

    p1 = Process(target=tcp, args=(pipe1, tcpPort))
    p2 = Process(target=bt, args=(pipe2, comPort))

    p1.start()
    p2.start()

    p1.join()
    p2.join()
