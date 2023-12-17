from typing import Literal
from toolbox import array, json, Enum, is_number, console
from dataclasses import dataclass, field
from re import search
import jieba

if __name__.__eq__('__main__'):
    from os import chdir
    from os.path import dirname, realpath
    chdir(dirname(realpath(__file__)))

from os import chdir
from os.path import dirname, realpath
chdir(dirname(realpath(__file__)))

jieba.load_userdict('userdict.txt')
    
class Context:

    class const(Enum):

        contains = lambda text, cat: any((CHI in text) if not isinstance(CHI, tuple) else any(cn in text for cn in CHI) for CHI in cat)
        translate = lambda text, cat: list(
            ENG for CHI, ENG in zip(cat.CHI, cat.ENG)
                if (
                    (CHI in text)
                        if not isinstance(CHI, tuple) else
                    any((chi in text) for chi in CHI)
                )
        ).pop()

        category = json({
            'direction': {
                'CHI': array('前', '後', '左', '右', '上', '下', ('順時針', '順時鐘'), ('逆時針', '逆時鐘')),
                'ENG': array('forward', 'backward', 'left', 'right', 'up', 'down', 'clockwise', 'c-clockwise')
            },
            'action': {
                'CHI': array('迴轉', ('懸停', '盤旋'), ('煞車', '暫停'), ('旋轉', '轉向'), '翻', ('垂降', '降落'), '迫降'),
                'ENG': array('return', 'hover', 'brake', 'spin', 'roll', 'land', 'f-land')
            },
            'unit': {
                'CHI': array('公尺', ('公分', '單位'), '度'),
                'ENG': array('meter', 'centimeter', 'degree')
            }
        })

    def __init__(self, context:str):

        @dataclass
        class __context_prototype__:
            source:str|list
            standardize:array = field(default_factory=array)

        self.context = __context_prototype__(source=context)
        
        (   self.extract()
                .filter()
                .standardize()  )

    def extract(self):
        self.context.source = jieba.lcut(self.context.source)
        return self
    
    def filter(self):
        deprecated = ('然後')
        for i, text in enumerate(self.context.source):
            if text in deprecated: del self.context.source[i]
        return self

    def standardize(self):

        class package(str):
            
            def __init__(self, *args):
                super().__init__()
            
            @property
            def category(self):
                try: self.__category # @IgnoreException
                except AttributeError: self.__category = None
                finally: return self.__category

            @category.setter
            def category(self, value:Literal['direction', 'action', 'number', 'unit']):
                self.__category = value
            
            def classify(self, category:Literal['direction', 'action', 'number', 'unit']):
                self.__category = category
                return self

        contains = __class__.const.contains
        translate = __class__.const.translate
        category = __class__.const.category

        for text in self.context.source:
            match text:
                case _ if contains(text, category.direction.CHI):
                    info = package(translate(text, category.direction)).classify(category='direction')
                case _ if contains(text, category.action.CHI):
                    info = package(translate(text, category.action)).classify(category='action')
                case _ if contains(text, category.unit.CHI):
                    info = package(translate(text, category.unit)).classify(category='unit')
                case _:
                    info = package(search(r'\d+\.?\d*', text).group()).classify(category='number') if is_number(text) or any(is_number(chr) for chr in text) else None
            console.info('info:', info, f'<{info.category if info is not None else "NoneType"}>', mode='debug')
            self.context.standardize.append(info) if info is not None else ...
                        
        return self
    
    def fetch(self):
        return self.context.standardize

class Movements:

    @classmethod
    def execute(cls, context:str):

        cmdl = Context(context).fetch()
        console.debug(cmdl)