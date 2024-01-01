from io import StringIO
import sys

sys.stdout = logs = StringIO()

from os import chdir, getcwd
from os.path import dirname, realpath

chdir(dirname(realpath(__file__))) if not getcwd().endswith(dirname(realpath(__file__))) else ...

from collections import namedtuple
from dataclasses import dataclass, field
from toolbox import Gadget, Enum, console
from threading import Thread
from queue import Queue
import tkinter as tk

def input(prompt: str = ''):
    ...

class color(Enum):
    white = '#FFFFFF'
    black = '#000000'

class ControlPanel:

    def __new__(cls, *args, **kwargs):

        @dataclass
        class __frames__:
            console: tk.Frame = None
        
        @dataclass
        class __vars__:
            console: tk.StringVar = None

        @dataclass
        class __threads__:
            stdin: Thread = None
            stdout: Thread = None
        
        cls.frames = __frames__
        cls.vars = __vars__
        cls.threads = __threads__

        return super().__new__(cls)

    def __init__(self):

        self.root = tk.Tk(className='control panel')
        self.vars = self.vars(
            console = tk.StringVar()
        )
        self.threads = self.threads(
            stdin = Thread(target=self.console_monitor, name='stdin', daemon=True),
            stdout = Thread(target=self.console_update, name='stdout', daemon=True)
        )

        self.threads.stdin.start()
        self.threads.stdout.start()

        self.root.title('Tello Drone Control Panel')
        self.root.iconbitmap('icon.ico')
        self.root.geometry(Gadget.setGeometry(window=self.root))
        self.root.option_add('*font', ('Consolas', 12, 'normal'))

        self.__init_buildtree__()\
            .__init_position__()\
            .__init_behaviour__()


    def __init_buildtree__(self):
        self.frames = self.frames(
            console = tk.Label(self.root, fg=color.white, bg=color.black, justify='left', anchor=tk.NW, textvariable=self.vars.console)
        )

        return self

    def __init_position__(self):
        self.frames.console.grid(sticky=tk.NSEW)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        return self
    
    def __init_behaviour__(self):
        #self.root.bind_all('<Key>', self.console_update)
        #console.info('Bind!')

        return self
    
    def console_update(self):
        for _ in sys.stdout:
            self.vars.console.set(self.vars.console.get()+_)
        #self.vars.console.set(logs.getvalue())

    def console_monitor(self):
        for _ in sys.stdin:
            console.info('get:', _.strip())


window = ControlPanel()
window.root.mainloop()

sys.stdout = sys.__stdout__
console.log(logs.getvalue())