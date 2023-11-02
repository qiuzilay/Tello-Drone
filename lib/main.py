from typing import Callable
from toolbox import Gadget, console
from time import sleep
from datetime import datetime
import socket
import cv2

class Main:

    def __init__(self, const):
        class __response_prototype: # 儲存無人機回傳的訊息。(在 Main.recv() 那邊賦值)
            def __init__(self):
                self.__msg = ''
                self.ignore = False

            # 用 self.response.get 可以在取值的同時清除儲存值
            @property
            def get(self):
                final, self.__msg = self.__msg, ''
                return final
            
            # self.response.value 就只是一般的讀取/寫入
            # (其實沒必要，只是為了讓格式跟 self.response.get 相同)
            @property
            def value(self):
                return self.__msg
            
            @value.setter
            def value(self, value):
                if not self.ignore: self.__msg = value


        self.sock: socket.socket # 註記 self.sock 等等會拿到 socket.socket 的類別物件 (寫給 vscode 看的)
        self.stream: cv2.VideoCapture # 註記 self.stream 等等會拿到 cv2.VideoCapture 的物件
        self.power = True # 控制 while 迴圈的開關 (之前因為不知道threading有daemon可以控制同步關閉才加了這東西)
        self.queue = list() # 指令佇列。Main.load() 讀取的指令都會塞進這裡等待 Main.exec() 處理
        self.sock = const.sock # 在這邊才正式給 self.sock 賦值
        self.stream = const.stream # 拿 cv2.VideoCapture 物件
        self.addr = const.addr # 拿位址集 (class addr)
        self.response = __response_prototype() # 因為 @property 只能用在物件上，所以這邊把 __response_prototype 實例化

    # 執行核心
    # (因為 Main.console() 跟 Main.execute() 這部分的功能重疊)
    # (所以把這部分從原先的 Main.execute() 中獨立出來)
    def _execore(self, cmdl:tuple, caller:Callable, ignore:bool=False):
        ###---- valid cmdl -----###
        # (command)               #
        # (command, value)        #
        # (command, value, delay) #
        # (command,, delay)       #
        ###---------------------###
        args:None
        class args:
            command = None
            value = None
            delay = None
        match len(cmdl):
            case 1:
                args.command, = cmdl
            case 2:
                args.command, args.value = cmdl
            case 3:
                args.command, args.value, args.delay = cmdl
            case _:
                raise ValueError('illegal number of arguments occurred at Main.execute()')
        
        # print 出準備送出的指令資訊
        console.info(
            f"\u2714 {'Loaded' if (caller.__name__.__ne__('console')) else 'Console'} commands: {args.command}",
            f"- value: {args.value if (args.value) else 'unspecified'}",
            f"- delay: {args.delay if (args.delay) else 'unspecified'}",
            f"- from: {caller.__name__}", sep='\n', end='\n\n'
        )
        self.response.ignore = ignore # 是否要 self.response 忽略記錄無人機回傳的消息
        self.send(args.command if (not args.value) else f'{args.command} {args.value}') # 發送指令至無人機

        return args

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
            args = self._execore(
                cmdl = self.queue[0],
                caller = self.execute
            )

            # 這段是用來防止指令發生碰撞被吃導致後面的動作大亂而添加的保險
            while True: # 重複檢測，直到取得來自無人機的回應(response)
                if self.response.value:

                    console.info('response:', self.response.value)

                    # 'error not joystick' 是無人機接收指令時若發生衝突會回傳的訊息
                    if not self.response.get.lower().__eq__('error not joystick'): # 如果無碰撞，進入 if 程式區塊
                        self.queue.pop(0) # 把佇列中最前面 (當前) 的指令移除
                        sleep(args.delay) if args.delay else ... # 如果該指令有設定延遲，處理延遲
                    else:
                        # 發生碰撞，發送訊息，且不將指令從佇列中移除
                        console.load(console.info, f'Congestion occurred. Would try to re-execute the command "{args.command}" in 3 seconds')

                    break # 離開此迴圈，回到 Main.execute() 的開頭

                else: sleep(0.1)

    # 載入器 (負責讀取'commands.txt'內的指令清單，並存入佇列中)
    def load(self):
        with open('./commands.txt', mode='r', encoding='UTF-8') as _cmdfile:
            for line in _cmdfile:
                if not line.startswith('#'):
                    self.queue.append(Gadget.formatter(line, split=','))

        console.info(
            f"Command list loaded successfully!",
            ''.center(32, '-'),
            '- ' + ('\n- '.join(map(str, self.queue))),
            ''.center(32, '-'), sep='\n'
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
                    
                    match userInput:
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
                            console.info('cv2.VideoCapture():', self.stream.isOpened())
                        case '!reload':
                            console.info('Reload the "commands.txt"')
                            self.load()
                        case '!clear':
                            self.queue = list()
                            console.info('All commands in the queue were cleared', end='\n\n')
                        case '!stop':
                            self.send('emergency')
                            raise CommandOverrideException # @IgnoreException
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
                self.queue = list()
                self.sock.close()
                console.info('Tello was forced to land cause an overriding command was triggered')
                break

    # 將指令發送給無人機
    def send(self, cmdl:str):
        try:
            self.sock.sendto(cmdl.encode(encoding='UTF-8'), self.addr.tello) # @IgnoreException
        except Exception as _E:
            console.warn(_E)

    # 讀取無人機回傳的影像資料
    def recvideo(self):
        while self.power: # 最外層迴圈 (因為是設計讓鏡頭可以開開關關)
            while self.stream.isOpened():
                # 有影像串流再執行內層迴圈
                # 無人機回傳的是 影像檔(image) 而不是 影片檔(video)
                # 所以假設如果要 60fps 就等於要讓這迴圈 1 秒跑 60 次。
                try:
                    # 由 cv2.VideoCapture 解析它拿到影像
                    _, frame = self.stream.read() # @IgnoreException
                    # cv2 創建視窗顯示影像。視窗名設為'Tello'
                    cv2.imshow('Tello', frame) # @IgnoreException

                    ## ----------- ##
                    # Enter -> 13   #
                    # Space -> 32   #
                    # Esc   -> 27   #
                    ## ----------- ##

                    # cv2.waitkey(16) 會讓視窗停佇 16 毫秒 (60fps = 1frame / 16.6ms)
                    # 期間如果 Enter 鍵被按下則進入 if 區塊
                    if (cv2.waitKey(16) & 0xFF).__eq__(13):
                        T = datetime.now() # 取得需要用在影像檔的檔名上的時間
                        path = (
                            fr'../screenshots/'
                            fr'{T.year}-{T.month}-{T.day} {T.hour}.{T.minute}.{T.second}.{str(T.microsecond)[0]}.jpg'
                        )
                        console.info(f'Save screenshots to', path)
                        # 斷言，如果 cv2.imwrite() 回傳 False（即儲存失敗）則觸發 AssertionError
                        assert cv2.imwrite(path, frame), "Failed to save the screeshots"
                        
                except Exception as _:
                    console.info(_)

            self.stream.release() # 關閉鏡頭
            cv2.destroyAllWindows() # 摧毀所有 cv2 創建的視窗

    # 接收無人機回傳的訊息
    def recv(self):
        while self.power:
            try:
                retval, _ = self.sock.recvfrom(1518) # @IgnoreException
                self.response.value = retval.decode()
            except Exception as _:
                console.info(_)
    

class CommandOverrideException(Exception): # 只是一個自定義的例外類別
    
    def __init__(self):
        self.message = 'Tello was forced to land cause an overriding command was triggered.'
        super().__init__(self.message)