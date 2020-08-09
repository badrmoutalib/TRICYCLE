import socket
import time
import struct
import signal
import sys
import math
 
code_sync_1 = 'A'
code_sync_2 = 'Z'
 
# set the speed of the two wheels
try:
    speed_left = float(sys.argv[1])
    speed_right = float(sys.argv[2])
except:
    speed_left = 0.0
    speed_right = 0.0
 
# set address and port for the socket communication
server_address_port = ('localhost', 33211)
 
# interrupt handler
def interrupt_handler(signal, frame):
    print ('You pressed CTRL-C, end of communication with V-REP robot')
    time.sleep(0.5)
    try:
        sock.close()
    except:
        print (sock,"socket already closed")
    sys.exit(0)
 
# trap hit of ctrl-C to stop the communication with V-REP
signal.signal(signal.SIGINT, interrupt_handler)
 
# client connects to server every 50 ms
loop_duration = 0.050
while True:
    # Create a TCP/IP socket
    t0 = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(server_address_port)
    except:
        print ("Cannot connect to server")
        break
 
    sock.settimeout(0.1) # set connection timeout
    # pack command
    strSend = struct.pack('<BBff',ord(code_sync_1),ord(code_sync_2),speed_left,speed_right)
    # send command to V-REP
    sock.sendall(strSend)
 
    # wait for status back from V-REP
    data = b''
    nch_rx = 14 # expect receiving 14 bytes from  V-REP 
    try:
        while len(data) < nch_rx:
            data += sock.recv(nch_rx)
    except:
        print ("socker error , duration is %f ms, try to reconnect !!!"%((time.time() - t0)*1000.0))
    # unpack the received data
    data_ok = False
    if len(data) == nch_rx:
        vrx = struct.unpack('<ccfff',data)
        if vrx[0] == b'A' and  vrx[1] == b'Z':
            data_ok = True
    else:
        pass
 
    sock.close()
    tsock = (time.time() - t0)*1000.0
 
    if data_ok:
        print ("sockect time=%.1f ms, simTime=%.2f s, left angle=%.1f, right angle=%.1f"%
               (tsock,vrx[2],vrx[3]*180.0/math.pi,vrx[4]*180.0/math.pi))
    else:
        print ("tsock",tsock,"ms, bad data !!")
 
    tsleep = loop_duration - (time.time()-t0)
    if tsleep>0:
        time.sleep (tsleep)  