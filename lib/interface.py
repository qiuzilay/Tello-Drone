from os import chdir, getcwd
from os.path import dirname, realpath

chdir(dirname(realpath(__file__))) if not getcwd().endswith(dirname(realpath(__file__))) else ...

from collections import namedtuple
from dataclasses import dataclass, field
from toolbox import Gadget, console
import tkinter

class window: ...

window:tkinter.Tk = tkinter.Tk(className='control panel')

window.title('Tello Drone Control Panel')
window.iconbitmap('icon.ico')
window.geometry(Gadget.setGeometry(window=window))

window.mainloop()