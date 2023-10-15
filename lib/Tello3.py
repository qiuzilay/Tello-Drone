import threading 
import socket
import sys
import time
from toolbox import Gadget, console
from os import chdir, path
from main import Main

chdir(path.dirname(path.realpath(__file__)))

class EventHandler: ...
class const:
    host = ''
    port = 9000
    tello_addr = ('192.168.10.1', 8889)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

EventHandler:Main = Main(const)


recvThread = threading.Thread(target=EventHandler.recv)
recvThread.start()

EventHandler.load()

execThread = threading.Thread(target=EventHandler.execute)
execThread.start()

EventHandler.console()

console.info('Ending')