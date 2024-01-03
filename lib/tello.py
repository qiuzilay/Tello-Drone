import socket
import cv2
from threading import Thread
from os import chdir, path
from typing import Literal
from toolbox import cmdl, console
from listener import Listener
from main import Main

chdir(path.dirname(path.realpath(__file__)))

console.mode = 'debug'
mode: Literal['connect', 'simulate'] = 'connect'

class Tello: ...
class const:
    
    class addr_prototype:
        global mode
        host = ('0.0.0.0', 9000)
        tello = ('192.168.10.1', 8889)
        stream = 'udp://@0.0.0.0:11111?overrun_nonfatal=1&fifo_size=50000000' if mode.__eq__('connect') else 0 # 無人機的影像傳輸位址
    addr = addr_prototype

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(addr.host)
    #console.info('Trying to connect with default webcam, please wait for a while...')
    stream = ... #cv2.VideoCapture(addr.stream)
    #console.info('Successed' if stream.isOpened() else 'Failed to connect your webcam, the function of video stream would not execute during this runtime.')

    mode = mode

Tello:Main = Main(const)

recvThread = Thread(name='Response Receiver', target=Tello.recv, daemon=True)
recvThread.start()

Tello.queue.put_nowait(cmdl(command='command', value=None, delay=0.1)) # （指令, 指令參數, 延遲秒數）
Tello.queue.put_nowait(cmdl(command='streamon', value=None, delay=0.1))

if False: #const.stream.isOpened():
    recvideoThread = Thread(name='Frame Receiver',target=Tello.recvideo, daemon=True)
    recvideoThread.start()

Tello.load()

execThread = Thread(name='Command Executor', target=Tello.execute, daemon=True)
execThread.start()

keyListener = Thread(name='EventListener', target=Listener.execute, daemon=True, args=[Tello])
keyListener.start()

cnslThread = Thread(name='Console Monitor', target=Tello.monitor, daemon=True)
cnslThread.start()

Tello.console()

console.info('Ending')