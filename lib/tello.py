import socket
import cv2
from threading import Thread
from pynput import keyboard
from time import sleep
from os import chdir, path
from random import choices
from typing import Literal
from toolbox import cmdl, console
from main import Main
from speaker import Event

chdir(path.dirname(path.realpath(__file__))) # 設定終端執行位置為此程式所在之資料夾

console.debug = True
mode:Literal['connect', 'simulate'] = 'simulate'

class Tello: ... # 只是變色用
class const: # 常數 (參數) 集。只是為了讓變數可以像 javascript 的 json 的存取寫法才刻意寫成這樣
    
    class addr_prototype: # 位址集。假如要存取 host，可以直接用 const.addr_prototype.host 讀取
        global mode
        host = ('0.0.0.0', 9000) # 電腦與無人機連線的 (UDP/IP, 埠號)
        tello = ('192.168.10.1', 8889) # 無人機與電腦連線的 (UDP/IP, 埠號)
        stream = 'udp://@0.0.0.0:11111' if mode.__eq__('connect') else 0 # 無人機的影像傳輸位址
    addr = addr_prototype # 讓變數集變回普通變數的顏色 (淺藍色)
    # 把變數集的 className 加個 prototype 在後面是因為如果直接用 addr，
    # "const.addr.host" 中會有兩個變數持有類別的顏色 (const and addr)
    # 但這樣就會跟 javascript 的 json 外貌不一樣
    # 所以 class 的名字才特意宣告成不同的樣子，之後再讓一般變數顏色的 addr 去指向它
    # 沒戳，只是為了美觀 (X

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    stream = cv2.VideoCapture(addr.stream) # 從給定的位址，捕捉影像。因為同樣在 const 內，所以這邊存取 addr 不用打 const
    sock.bind(addr.host)

    mode = mode


T = 3 # 如果 VideoCapture 捕捉失敗，重新嘗試連線。(雖然如果第一次失敗後面再試幾次極大概率也不會成功啦 030)
for _ in range(T) if not const.stream.isOpened() else ():
    console.info(f'cv2.VideoCapture failed to initialize. {T-_} retrying {"chance" if _ <= 1 else "chances"} left.')
    if const.stream.open(const.addr.stream):
        break
    else: sleep(1) if (_ + 1 < T) else console.info(f'Failed to initial camera!')

# 把參數集送進 main.py 裡面的 Main 類別裡面，創建實例，命名Tello。Main 的所有內容請至 main.py 查看。
Tello:Main = Main(const)

# 創建新執行緒 (多工/並行處理)，執行 Main 下方的 recv() 方法
recvThread = Thread(target=Tello.recv, daemon=True)
recvThread.start() # 開始執行

# 將 command 和 streamon 兩個指令添加進指令隊列，待會供 Main.exec() 執行，為傳給無人機讓其在最一開始時執行。
# 兩個指令作用請參見 sources 資料夾內的 "Tello SDK 2.0 User Guide.pdf" 內的說明
Tello.queue.append(cmdl(command='command', value=None, delay=0.1)) # （指令, 指令參數, 延遲秒數）
Tello.queue.append(cmdl(command='streamon', value=None, delay=0.1))

if const.stream.isOpened(): # 如果 cv2.VideoCapture 有成功啟動，才建立接收影像用的執行緒，否則跳過。
    recvideoThread = Thread(target=Tello.recvideo, daemon=True)
    recvideoThread.start()

Tello.load() # 即 Main.load()，載入 "commands.txt" 內設定的指令

execThread = Thread(target=Tello.execute, daemon=True) # Main.execute() 的執行緒
execThread.start()

keyListener = keyboard.Listener(on_press=Event.on_press, on_release=Event.on_release)
keyListener.daemon = True
keyListener.start()

Tello.console() # 由主程式處理(監聽)自終端機輸入的指令

console.info('Ending') # 主程序終止