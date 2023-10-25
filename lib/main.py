from typing import Iterable, Sequence, Callable
from toolbox import Gadget, console
from time import sleep
import socket
import cv2

class Main:

    def __init__(self, const):
        class __response_prototype:
            def __init__(self):
                self.__msg = ''

            @property
            def get(self):
                final, self.__msg = self.__msg, ''
                return final
            
            @property
            def value(self):
                return self.__msg
            
            @value.setter
            def value(self, value):
                self.__msg = value


        self.sock: socket.socket
        self.stream: cv2.VideoCapture
        self.power = True
        self.queue = list()
        self.sock = const.sock
        self.stream = const.stream
        self.addr = const.addr
        self.response = __response_prototype()

    def _execore(self, cmdl:tuple, caller:Callable):
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
            
        console.info(
            f"\u2714 {'Loaded' if (caller.__name__.__ne__('console')) else 'Console'} commands: {args.command}",
            f"- value: {args.value if (args.value) else 'unspecified'}",
            f"- delay: {args.delay if (args.delay) else 'unspecified'}",
            f"- from: {caller.__name__}", sep='\n', end='\n\n'
        )
        self.send(args.command if (not args.value) else f'{args.command} {args.value}')

        return args

    def execute(self):
        # console.load(console.info, 'Function.exec() is executing now')
        while self.power:
            if not self.queue:
                sleep(1)
                continue
            self.queue[0]
            args = self._execore(
                cmdl = self.queue[0],
                caller = self.execute
            )
            console.info('response:', self.response.value)
            if not self.response.get.lower().__eq__('error not joystick'):
                self.queue.pop(0)
                sleep(args.delay) if args.delay else ...
            else:
                console.info(f'Congestion occurred. Would try to re-execute the command "{args.command}" in 0.5 seconds')
                sleep(0.5)

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
                    #self.queue.insert(0, Gadget.formatter(userInput, split=','))
                    self._execore(
                        cmdl = Gadget.formatter(userInput, split=','),
                        caller=self.console
                    )

            except KeyboardInterrupt:
                self.power = False
                self.sock.close()
                console.info('Socket was closed cause the exception "KeyboardInterrupt" was triggered')
                break

            except CommandOverrideException:
                self.power = False
                self.queue = list()
                self.send('land')
                console.info('Tello was forced to land cause an overriding command was triggered')
                self.sock.close()
                break

    #---------------- Custom Functions END ----------------#

    def send(self, cmdl:str):
        try:
            self.sock.sendto(cmdl.encode(encoding='UTF-8'), self.addr.tello) # @IgnoreException
        except Exception as _E:
            console.warn(_E)

    def recvideo(self):
        cv2.CAP_PROP_FRAME_WIDTH
        while self.power:
            while self.stream.isOpened():
                try:
                    _, frame = self.stream.read() # @IgnoreException
                    cv2.imshow('Tello', frame) # @IgnoreException
                    #cv2.imshow("Tello", cv2.resize(frame, (
                    #    int(self.stream.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    #    int(self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    #))) # @IgnoreException
                    cv2.waitKey(16)
                except Exception as _:
                    console.info(_)
            self.stream.release()
            cv2.destroyAllWindows()

    def recv(self):
        while self.power:
            try:
                retval, _ = self.sock.recvfrom(1518) # @IgnoreException
                self.response.value = retval.decode()
                console.log('<Tello>', self.response.value, end='\n\n')
            except Exception as _:
                console.info(_)
    

class CommandOverrideException(Exception):
    
    def __init__(self):
        self.message = 'Tello was forced to land cause an overriding command was triggered.'
        super().__init__(self.message)