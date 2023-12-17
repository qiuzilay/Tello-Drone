import tkinter
from collections import namedtuple
from dataclasses import dataclass, field
from toolbox import Gadget, console

class window: ...

window:tkinter.Tk = tkinter.Tk(className='control panel')

window.title('Control Panel')
window.geometry(Gadget.setGeometry(window=window))

window.mainloop()