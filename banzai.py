from multiprocessing import Process, Pipe
from multiprocessing.connection import Connection
import socket
import time

def tcp(pipeConn: Connection):
    print("tcp!")
    print(pipeConn)
    HOST = '127.0.0.1'  # Localhost
    PORT = 65432

    # Create a socket object
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print(f'Server listening on {HOST}:{PORT}')
        
        # Wait for a connection
        tcpConn, addr = s.accept()
        with tcpConn:            
            print(f'Connected by {addr}')            
            while True:
                data = pipeConn.recv()
                if not data:
                    break
                print(f'data={data}')        
                tcpConn.sendall(data)    


def bt(pipeConn: Connection):
    print('bt!')
    print(pipeConn)
    with open(r"D:\code\gps-nmea-log-files\TrimbleR1_20160310-165531.txt", 'r') as file:
        sentences = [bytes(l.rstrip()  + '\r\n', 'utf-8') for l in file.readlines()]
    while True:
        data = sentences.pop(0)
        sentences.append(data)    
        pipeConn.send(data)  
        time.sleep(1)
  

def btBAD():
    import sys
    import bluetooth
    addr = None

    # if len(sys.argv) < 2:
    #     print("No device specified. Searching all nearby bluetooth devices for "
    #         "the SampleServer service...")
    # else:
    #     addr = sys.argv[1]
    #     print("Searching for SampleServer on {}...".format(addr))

    # # search for the SampleServer service
    # uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
    # service_matches = bluetooth.find_service(uuid=uuid, address=addr)

    # if len(service_matches) == 0:
    #     print("Couldn't find the SampleServer service.")
    #     sys.exit(0)

    nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True,
                                            flush_cache=True, lookup_class=False)
    device_match = [(addr, name) for (addr, name)  in nearby_devices if name == 'HC-06']
    first_match = service_matches[0]
    port = first_match["port"]
    name = first_match["name"]
    host = first_match["host"]

    print("Connecting to \"{}\" on {}".format(name, host))

    # Create the client socket
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((host, port))

    print("Connected. Type something...")
    while True:
        data = sock.recv()
        #data = input()
        if not data:
            break
        #sock.send(data)
        q1.put(data)
        # if q1.get(timeout=)
    sock.close()

if __name__ == '__main__':

    pipe1, pipe2 = Pipe()

    p1 = Process(target=tcp, args=(pipe1, ))
    p2 = Process(target=bt, args=(pipe2, ))

    p1.start()
    p2.start()

    p1.join()
    p2.join()
