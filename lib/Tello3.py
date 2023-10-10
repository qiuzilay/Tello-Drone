import threading 
import socket
import sys
import time
from toolbox import Gadget, console
from os import chdir, path
from main import CustomFunc as Function
from main import CommandOverrideException

chdir(path.dirname(path.realpath(__file__)))

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
            console.info("Exit from recv() since an unknown exception was triggered")
            break

def send(cmd:str):
    try:
        sock.sendto(cmd.encode(encoding="utf-8"), tello_address)
        #console.log(f"Execute commands: {cmd}, set exec time as {delay} second{'s' if delay > 1 else ''}")
    except Exception as _E:
        console.warn(_E)

cmdl = list()
Function.load(cmdl)

#console.info(*cmdl, sep='\n')


recvThread = threading.Thread(target=recv)
recvThread.start()


while True: 

    try:
        cmd = input("<Tello> ")

        if not cmd or 'end' in cmd:
            sock.close()
            console.info("Socket was closed")
            break

        if cmd.startswith('/'): # commands trigger
            
            match cmd:
                case '/reload':
                    Function.load(cmdl)
                case '/land':
                    send('land')
                    raise CommandOverrideException
                case _:
                    console.info(f'The command "{cmd[1:]}" was not found')

        else:
            send(cmd)

    except KeyboardInterrupt:
        sock.close()
        console.info("Socket was closed cause the exception 'KeyboardInterrupt' was triggered")
        break

    except CommandOverrideException:
        sock.close()
        console.info("Tello was forced to land cause an overriding command was triggered")
        console.load(console.info, 'Landing')
        break

console.info("Ending")