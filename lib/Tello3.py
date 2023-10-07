import threading 
import socket
import sys
import time
from toolbox import Gadget, console


host = ''
port = 9000
locaddr = (host, port) 



sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tello_address = ('192.168.10.1', 8889)

sock.bind(locaddr)



def recv():
    count = 0
    while True:
        try:
            data, server = sock.recvfrom(1518)
            data.decode(encoding="utf-8")
            #print(data.decode(encoding="utf-8"))
        except Exception:
            console.info("Exit from recv() since an unknown exception was triggered.")
            break

def send(cmd:str):
    try:
        sock.sendto(cmd.encode(encoding="utf-8"), tello_address)
        #console.log(f"Execute commands: {cmd}, set exec time as {delay} second{'s' if delay > 1 else ''}")
    except Exception as _E:
        console.warn(_E)


"""def send(cmd:str, delay:int|float=0):
    delay in seconds
    try:
        sock.sendto(cmd.encode(encoding="utf-8"), tello_address)
        console.log(f"Execute commands: {cmd}, set exec time as {delay} second{'s' if delay > 1 else ''}")
    except Exception as _E:
        console.warn(_E)

    time.sleep(delay)"""

"""print ('\r\n\r\nTello Python3 Demo.\r\n')

print ('Tello: command takeoff land flip forward back left right \r\n       up down cw ccw speed speed?\r\n')

print ('end -- quit demo.\r\n')"""



recvThread = threading.Thread(target=recv)
recvThread.start()

while True: 

    try:
        cmd = input("<Tello> ")

        if not cmd or 'end' in cmd:
            sock.close()
            console.info("socket was closed.")
            break

        else:
            send(cmd)

    except KeyboardInterrupt:
        sock.close()
        console.info("socket was closed cause the exception 'KeyboardInterrupt' was triggered.")
        break

console.info("Ending.")