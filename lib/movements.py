from typing import Literal
from toolbox import array, json, Enum, is_number, console
from dataclasses import dataclass, field
from re import search
from json import load
from os import chdir, getcwd
from os.path import dirname, realpath
import jieba

chdir(dirname(realpath(__file__))) if not getcwd().endswith(dirname(realpath(__file__))) else ...

jieba.load_userdict('./configs/userdict.txt')
with open('./configs/categories.json', encoding='UTF-8') as categories: fetch = json(load(categories))
    
class Context:

    class const(Enum):

        category = fetch.category
        deprecated = fetch.deprecated

    def __init__(self, context:str):

        @dataclass
        class __context_prototype__:
            source:str|list
            metadata:array = field(default_factory=array)
            final:array = field(default_factory=array)

        self.context = __context_prototype__(source=context)
        
        self.extract().standardize()

    def extract(self):
        self.context.source = jieba.lcut(self.context.source)
        return self

    def standardize(self):

        class metadata(str):

            def __init__(self, *args):
                super().__init__()

            def config(self, priority:int=..., weight:int=..., match:str=..., category:Literal['position', 'action', 'number', 'unit']=...):
                self.priority = priority
                self.weight = weight
                self.match = match
                self.category = category
                return self

        def translator(text) -> metadata | None:
            info = None
            if text in self.const.deprecated: return
            elif any(is_number(chr) for chr in text):
                info = metadata(search(r'\d+\.?\d*', text).group()).config(
                    priority = 0,
                    weight = 0,
                    category = 'number'
                )
            else:
                ctg: json; attr: json
                for NAME, ctg in self.const.category.items():
                    for ENG, attr in ctg.items():
                        for CHI in attr.associate:
                            if CHI in text:
                                info = metadata(ENG).config(
                                    priority = attr.priority,
                                    weight = attr.weight,
                                    match = CHI,
                                    category = NAME
                                ) if (info is None) or (info.priority < attr.priority) or (len(info.match) < len(CHI)) else info
                                break
            return info

        for text in self.context.source:
            info = translator(text)
            console.info('info:', info, f'<{info.category if info is not None else "NoneType"}>', mode='debug')
            self.context.metadata.append(info) if info is not None else ...
                        
        return self
    
    def fetch(self):

        @dataclass
        class bundle:
            position: str
            action: str
            value: int | float
            unit: str

        metadata = self.context.metadata
        group = array()
        for i, _ in enumerate(self.context.metadata):
            data = metadata.shift()
            if group.all(lambda val: val.category != data.category):
                group.append(data)
                continue
            
            for item in group: ...
            
            

class Movements:

    @classmethod
    def execute(cls, context:str):
        source = Context(context).context.source
        metadata = Context(context).context.metadata
        console.debug(source)
        console.debug(metadata)