from toolbox import console, Enum, array, json, String
from json import load
from os import chdir, getcwd
from os.path import dirname, realpath
from dataclasses import dataclass, field
from collections import namedtuple
from movements import Movements

chdir(dirname(realpath(__file__))) if not getcwd().endswith(dirname(realpath(__file__))) else ...

arr = array(['往前', '飛行', '30', '公尺', '然後', '順時針', '旋轉', '90', '度']).join()
context = '左轉飛行3公尺懸停10秒順時針旋轉90度降落'
Movements.read(context)