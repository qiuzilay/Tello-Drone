from typing import Iterable, Sequence, Callable
from toolbox import Gadget, console
from time import sleep

class Main:

    def __init__(self, const):
        self.power = True
        self.queue = list()
        self.sock = const.sock
        self.tello_addr = const.tello_addr

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
            delay = 0
        match len(cmdl):
            case 1:
                args.command, = cmdl
            case 2:
                args.command, args.value = cmdl
            case 3:
                args.command, args.value, args.delay = cmdl
            case _:
                raise ValueError('illegal number of arguments occurred at Main.execute()')
            
        self.send(args.command if (not args.value) else f'{args.command} {args.value}')
        console.info(
            f"\u2714 {'Loaded' if (caller.__name__.__ne__('console')) else 'Console'} commands: {args.command}",
            f"- value: {args.value if (args.value) else 'unspecified'}",
            f"- delay: {args.delay if (args.delay) else 'unspecified'}",
            f"- caller: {caller.__name__}", sep='\n', end='\n\n'
        )

        return args

    def execute(self):
        # console.load(console.info, 'Function.exec() is executing now')
        while self.power:
            if not self.queue:
                sleep(1)
                continue
            args = self._execore(
                cmdl = self.queue.pop(0),
                caller = self.execute
            )
            if args.delay: sleep(args.delay)

    
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
        )
    

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
                        case '!reload':
                            console.info('Reload the "commands.txt"')
                            self.load()
                        case '!clear':
                            self.queue = list()
                            console.info('All commands in the queue were cleared', end='\n\n')
                        case '!stop':
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
            self.sock.sendto(cmdl.encode(encoding='UTF-8'), self.tello_addr)
        except Exception as _E:
            console.warn(_E)

    def recv(self):
        while self.power:
            try:
                data, server = self.sock.recvfrom(1518) # @IgnoreException
                data.decode(encoding='UTF-8')
                #print(data.decode(encoding="utf-8"))
            except Exception:
                console.info('Exit from recv() since an unknown exception was triggered')
                break
    

class CommandOverrideException(Exception):
    
    def __init__(self):
        self.message = 'Tello was forced to land cause an overriding command was triggered.'
        super().__init__(self.message)