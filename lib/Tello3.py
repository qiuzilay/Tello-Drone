import threading 
import socket
import sys
from time import sleep
import cv2
from toolbox import Gadget, console
from os import chdir, path
from main import Main

chdir(path.dirname(path.realpath(__file__)))

class Tello: ...
class const:
    class addr:
        host = ('0.0.0.0', 9000)
        tello = ('192.168.10.1', 8889)
        stream = 'udp://@0.0.0.0:11111'

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    stream = cv2.VideoCapture(addr.stream)
    sock.bind(addr.host)


T = 3
for _ in range(T) if not const.stream.isOpened() else ():
    console.info(f'cv2.VideoCapture failed to initialize. {T-_} retrying {"chance" if _ <= 1 else "chances"} left.')
    if const.stream.open(const.addr.stream):
        break
    else: sleep(1) if (_ + 1 < T) else console.info(f'Failed to initial camera!')


Tello:Main = Main(const)


recvThread = threading.Thread(target=Tello.recv)
recvThread.daemon = True
recvThread.start()

Tello.queue.append(('command', None, 0.1))
Tello.queue.append(('streamon', None, 0.1))

if const.stream.isOpened():
    recvideoThread = threading.Thread(target=Tello.recvideo)
    recvideoThread.daemon = True
    recvideoThread.start()

Tello.load()

execThread = threading.Thread(target=Tello.execute)
execThread.daemon = True
execThread.start()

Tello.console()

console.info('Ending')