from toolbox import console, Enum, array, json, String
from json import load
from os import chdir, getcwd
from os.path import dirname, realpath
from dataclasses import dataclass, field
from movements import Movements

chdir(dirname(realpath(__file__))) if not getcwd().endswith(dirname(realpath(__file__))) else ...

"""with open('./configs/userdict.txt', mode='w', encoding='UTF-8') as ctgfile:

    category = json(load(open('./configs/categories.json', encoding='UTF-8')))

    console.debug(category)

    get = array()

    for ctg_name, ctg in category.items():
        for name, info in ctg.items():
            for CHI in info.associate:
                get.append(CHI)

    ctgfile.writelines(get.join('\n'))"""

#arr = array(['往前', '飛行', '30', '公尺', '然後', '順時針', '旋轉', '90', '度'])
context = '左轉飛行3秒懸停10秒順時針旋轉90度降落'
Movements.read(context)