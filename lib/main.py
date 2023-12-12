from typing import Callable, Literal
from toolbox import Gadget, array, console
from time import sleep
from datetime import datetime
from threading import Thread
from random import choices, randint
from os import mkdir
from os.path import isdir, abspath
import socket
import cv2
import mediapipe

class MPipe:
    drawing = mediapipe.solutions.drawing_utils
    drawing_styles = mediapipe.solutions.drawing_styles
    holistic = mediapipe.solutions.holistic

class Main:

    def __init__(self, const):
        class __response_prototype: # 儲存無人機回傳的訊息。(在 Main.recv() 那邊賦值)
            def __init__(self):
                self.msgs = array()
                self.ignore = array()

            @property
            def value(self) -> str:
                return self.msgs[0]
            
            @value.setter
            def value(self, value):
                self.msgs.append(value.lower())

        self.power = True # 控制 while 迴圈的開關 (之前因為不知道threading有daemon可以控制同步關閉才加了這東西)
        self.recording = None # 錄製控制
        self.mode: Literal['connect', 'simulate'] = const.mode
        self.queue = array() # 指令佇列。Main.load() 讀取的指令都會塞進這裡等待 Main.exec() 處理
        self.sock: socket.socket = const.sock # 拿 socket.socket 物件
        self.stream:cv2.VideoCapture = const.stream # 拿 cv2.VideoCapture 物件
        self.addr = const.addr # 拿位址集 (class addr)
        self.response = __response_prototype() # 因為 @property 只能用在物件上，所以這邊把 __response_prototype 實例化

    # 執行核心
    # (因為 Main.console() 跟 Main.execute() 這部分的功能重疊)
    # (所以把這部分從原先的 Main.execute() 中獨立出來)
    def _execore(self, cmdl:tuple, caller:Callable, ignore:bool=False) -> tuple:
        ###---- valid cmdl -----###
        # (command)               #
        # (command, value)        #
        # (command, value, delay) #
        # (command,, delay)       #
        ###---------------------###
        
        # print 出準備送出的指令資訊
        console.log(''.center(32, '-'))
        console.info(
            f"\u2714 {'Loaded' if (caller.__name__.__ne__('console')) else 'Console'} commands: {cmdl.command}",
            f"- value: {cmdl.value if (cmdl.value) else 'unspecified'}",
            f"- delay: {cmdl.delay if (cmdl.delay) else 'unspecified'}",
            f"- from: {caller.__name__}", sep='\n'
        )
        self.response.ignore.append(ignore) # 是否要 self.response 忽略記錄無人機回傳的消息
        self.send(cmdl.command if (not cmdl.value) else f'{cmdl.command} {cmdl.value}') # 發送指令至無人機

        return cmdl

    # 執行器 (負責處理佇列中的指令)
    def execute(self):
        while self.power:
            # 如果沒指令佇列，等待一秒後再次進入迴圈
            if not self.queue:
                sleep(1)
                continue
            
            # 如果執行到這邊代表有指令存在於佇列中，開始處理

            # 把指令送進執行核心內，表明呼叫者是 Main.execute()
            # 最後再捕捉 Main._execore() 回傳的指令參數 (class args)
            cmdl = self._execore(
                cmdl = self.queue[0],
                caller = self.execute
            )

            # 這段是用來防止指令發生碰撞被吃導致後面的動作大亂而添加的保險
            while True: # 重複檢測，直到取得來自無人機的回應(response)
                if self.response.msgs.length:
                    console.info(
                        'status:',
                        '\t'f'response: {self.response.msgs} [{len(self.response.msgs)}]',
                        '\t'f'ignore: {self.response.ignore} [{len(self.response.ignore)}]',
                        sep='\n', mode='debug'
                    )
                    response = self.response.msgs.shift()
                    ignore = self.response.ignore.shift()
                    console.info('response:', response, f'[ignore: {ignore}]', mode='debug')
                    
                    if ignore: continue # 自 console 輸入的指令得到的對應回覆，忽略

                    # 'error not joystick' 是無人機接收指令時若發生衝突會回傳的訊息
                    if response != 'error not joystick': # 如果無碰撞，進入 if 程式區塊
                        self.queue.shift() # 把佇列中最前面 (當前) 的指令移除
                        sleep(cmdl.delay) if cmdl.delay else ... # 如果該指令有設定延遲，處理延遲
                    else:
                        # 發生碰撞，發送訊息。不將指令從佇列中移除
                        console.info(f'Congestion occurred. Would try to re-execute the command "{cmdl.command}" in 1 seconds')
                        sleep(1)

                    break # 離開此迴圈，回到 Main.execute() 的開頭

    # 載入器 (負責讀取'commands.txt'內的指令清單，並存入佇列中)
    def load(self):
        with open('./commands.txt', mode='r', encoding='UTF-8') as _cmdfile:
            for line in _cmdfile:
                if not line.startswith('#'):
                    self.queue.append(Gadget.formatter(line, split=','))

        console.info(
            f"Command list loaded successfully!",
            '- ' + self.queue.copy().each(Gadget.visualize).join('\n- '),
            sep='\n'
        ) if self.queue else console.info(f'Command list was empty.')
    
    # 終端機輸入監聽器
    def console(self):
        while self.power: 

            try:
                userInput = input()

                if not userInput or 'end' in userInput:
                    self.power = False
                    self.sock.close()
                    console.info('Socket was closed')
                    break

                elif userInput.startswith('!'): # commands prefix trigger
                    command, *args = Gadget.argsplit(userInput)
                    match command:
                        case '!test':
                            ...
                        case '!response':
                            console.info(self.response.value)
                        case '!frameinfo':
                            console.info('frame:', (
                                int(self.stream.get(cv2.CAP_PROP_FRAME_WIDTH)),
                                int(self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
                            ))
                        case '!stream':
                            self.stream.release() if self.stream.isOpened() else self.stream.open(self.addr.stream)
                            console.info(f'Video stream sent from Tello {"is starting" if self.stream.isOpened() else "was stopped"}.')
                            console.info('cv2.VideoCapture():', self.stream.isOpened(), mode='debug')
                        case '!reload':
                            console.info('Reload the "commands.txt"')
                            self.load()
                        case '!clear':
                            self.queue = array()
                            console.info('All commands in the queue were cleared', end='\n\n')
                        case '!stop':
                            self.send('emergency')
                            raise CommandOverrideException # @IgnoreException
                        case '!record':
                            self.recording = Thread(
                                target = self.record,
                                args = args,
                                daemon = True
                            )
                            self.recording.start()
                        case _:
                            console.info(f'The command "{userInput[1:]}" was not found!', end='\n\n')

                else:
                    # 不是空白，也不是'end'，沒有'!'前墜，那就視為要傳給無人機的指令
                    # 越過 Main.execute() 將指令強制餵給無人機，所以要 self.response 不要記錄回應
                    # 這設計可能有小瑕疵，畢竟是指令的發送和回應的接收是異步
                    # 如果 Main.execute() 跟 Main.console() 送出指令的時間太過接近大概會讓收到的回應內容錯亂
                    # 之後有空再改
                    self._execore(
                        cmdl = Gadget.formatter(userInput, split=','),
                        caller=self.console,
                        ignore=True
                    )

            # 強制關閉終端機會觸發此例外，終止程式
            except KeyboardInterrupt:
                self.power = False
                self.sock.close()
                console.info('Socket was closed cause the exception "KeyboardInterrupt" was triggered')
                break
            
            # 使用'!stop'會觸發此例外，終止程式
            except CommandOverrideException:
                self.power = False
                self.queue = array()
                self.sock.close()
                console.info('Tello was forced to land cause an overriding command was triggered')
                break

            except Exception as E: console.info(E)

    # 將指令發送給無人機
    def send(self, cmdl:str):
        if self.mode.__eq__('connect'):
            try:
                self.sock.sendto(cmdl.encode(encoding='UTF-8'), self.addr.tello) # @IgnoreException
            except Exception as E:
                console.info(E)
        else:
            sleep(randint(0, 1000)/1000)
            self.response.value = choices(('Error not joystick', 'OK'), weights=(1/3, 2/3))[0]
            
    # 讀取無人機回傳的影像資料
    def recvideo(self):

        def __core_recvideo(MPobj=...):
            nonlocal self
            try:
                _, frame = self.stream.read() # @IgnoreException

                MPipe.drawing.draw_landmarks(
                    frame,
                    MPobj.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).pose_landmarks,
                    MPipe.holistic.POSE_CONNECTIONS,
                    landmark_drawing_spec = MPipe.drawing_styles.get_default_pose_landmarks_style()
                ) if MPobj is not Ellipsis else ...

            except Exception as E:
                console.info(E)
            else:
                cv2.imshow('Tello', frame)
                ## ----------- ##
                # Enter -> 13   #
                # Space -> 32   #
                # Esc   -> 27   #
                ## ----------- ##
                if (cv2.waitKey(16) & 0xFF).__eq__(13):
                    T = datetime.now()
                    path = (
                        fr'../screenshots/' +
                        T.strftime(r"%Y-%m-%d %H.%M.%S.") + str(T.microsecond)[:3] + '.jpg'
                    )
                    console.info(f'Save screenshots to', path)
                    
                    console.info("Failed to save the screeshots") if not cv2.imwrite(path, frame) else ...

            finally: ...

        while self.power:
            try:
                with MPipe.holistic.Holistic( # @IgnoreException
                    min_detection_confidence = 0.5,
                    min_tracking_confidence = 0.5
                ) as holist:
                    while self.stream.isOpened(): __core_recvideo(holist)
            except Exception as E:
                console.info(E)
                while self.stream.isOpened(): __core_recvideo()

            self.stream.release()
            cv2.destroyAllWindows()

    # 接收無人機回傳的訊息
    def recv(self):
        while self.power:
            try:
                retval, _ = self.sock.recvfrom(1518) # @IgnoreException
                self.response.value = retval.decode()
            except Exception as _:
                console.info(_)
    
    # 擷取一連串的影像資料
    def record(self, quanty:int=10, intval:int|float=100):
        state = self.stream.isOpened()

        try:
            console.info(f'Start collecting several images then pack as an album. (quanty: {quanty} , intval: {intval})')
            self.stream.open(self.addr.stream) if not state else ...
            path = None
            i = 1
            while True:
                path = f'../screenshots/album-{i}'
                if isdir(path):
                    i += 1
                else:
                    mkdir(path)
                    break
            for i in range(1, quanty+1):
                _, frame = self.stream.read() # @IgnoreException
                assert cv2.imwrite(f'{path}/{i}.jpg', frame), "Failed to save the screeshots"
                sleep(intval/1000)

        except Exception as E:
            console.info(E)
        else:
            console.info(f'Successfully saved {quanty} {"images" if quanty > 1 else "image"} to {abspath(path)}')
        finally:
            self.stream.release() if state is False else ...
            self.recording = None

class CommandOverrideException(Exception): # 只是一個自定義的例外類別
    
    def __init__(self):
        self.message = 'Tello was forced to land cause an overriding command was triggered.'
        super().__init__(self.message)