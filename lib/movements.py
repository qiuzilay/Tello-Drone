from typing import Literal
from toolbox import array, slider, json, Enum, is_number, console
from dataclasses import dataclass, field
from collections import namedtuple as ntuple
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
        
        self.extract().standardize().bind()

    def extract(self):
        self.context.source = jieba.lcut(self.context.source)
        return self

    def standardize(self):

        class metadata(str):

            def __init__(self, *args):
                super().__init__()

            def config(self, type:Literal['length', 'scale', 'time']=..., pos:int=..., priority:int=..., weight:int=..., match:str=..., category:Literal['position', 'action', 'value', 'unit']=...):
                # generic attributes
                if priority is not Ellipsis: self.priority = priority
                if weight is not Ellipsis: self.weight = weight
                if category is not Ellipsis: self.category = category
                if match is not Ellipsis: self.match = match

                # for unit only
                if type is not Ellipsis: self.type = type

                # for index of each metadata located at self.context.metadata
                if pos is not Ellipsis: self.pos = pos

                return self

        def translator(text) -> metadata | None:
            info = None
            if text in self.const.deprecated: return
            elif any(is_number(chr) for chr in text):
                info = metadata(search(r'\d+\.?\d*', text).group()).config(
                    priority = 0,
                    weight = 0,
                    category = 'value'
                )
            else:
                ctg: json; attr: json
                for CTG, ctg in self.const.category.items():
                    for ENG, attr in ctg.items():
                        for CHI in attr.associate:
                            if CHI in text:
                                info = metadata(ENG).config(
                                    priority = attr.priority,
                                    weight = attr.weight,
                                    match = CHI,
                                    category = CTG
                                ) if (info is None) or (len(info.match) < len(CHI)) or (info.priority < attr.priority) else info
                                info.config(type=attr.type) if CTG.__eq__('unit') else ...
                                break
            return info

        for text in self.context.source:
            info = translator(text)
            #console.info('info:', info, f'<{info.category if info is not None else "NoneType"}>', mode='debug')
            self.context.metadata.append(info.config(pos=self.context.metadata.length)) if info is not None else ...
                        
        return self
    
    def bind(self):

        @dataclass
        class bundle:
            index: int
            action: str
            position: str = field(default=None)
            value: int | float = field(default=None)
            unit: str = field(default=None)

        @dataclass
        class dataset:
            action: array = field(default_factory=array)
            position: array = field(default_factory=array)
            value: array = field(default_factory=array)
            unit: array = field(default_factory=array)
        dataset = dataset()
        #dataset = self.context.metadata.copy(); prim_len = dataset.length
        #self.context.final = array(bundle(action=dataset.pop(metadata.pos - prim_len + dataset.length)) for metadata in self.context.metadata if metadata.category.__eq__('action'))
        for metadata in self.context.metadata:
            console.info(metadata, f'<{metadata.category}>')
            match metadata.category:
                case 'action': self.context.final.append(bundle(action=metadata, index=self.context.final.length))
                case 'position': dataset.position.append(metadata)
                case 'value': dataset.value.append(metadata)
                case 'unit': dataset.unit.append(metadata)
                case _: raise Exception(f'Unexpected Exception occurred caused by Context.context.metadata owns illegal category attribute: {metadata.category}')

        class window: ...
        class package: ...
        SIZE = 3
        window:slider = slider(size=SIZE)
        for package in [None, *self.context.final, None]:
            if window.append(package).length < SIZE: continue
            #index = i - (SIZE - 1)
            prev, this, next = window
            scope = ntuple('scope', ('left', 'right'))
            
            def between(target:Literal['<instance "metadata">']) -> tuple:
                nonlocal prev, this, next
                if prev is None:
                    if target.pos < next.action.pos:    
                        return scope(left=None, right=this) if target.pos < this.action.pos else scope(left=this, right=next)
                elif next is None:
                    if prev.action.pos < target.pos:
                        return scope(left=this, right=None) if this.action.pos < target.pos else scope(left=prev, right=this)
                elif prev.action.pos < target.pos < next.action.pos:
                    return scope(left=prev, right=this) if target.pos < this.action.pos else scope(left=this, right=next)
                
                return None

            # 'position'
            try:
                target = dataset.position[0]
                packs = between(target)
                if packs:
                    if packs.left is None or packs.right is None:
                        self.context.final[this.index].position = dataset.position.shift()
                    else:
                        if packs.left.position is None:
                            dist = scope(
                                left = abs(target.pos - packs.left.action.pos),
                                right = abs(target.pos - packs.right.action.pos)
                            )
                            if dist.left <= dist.right:
                                packs.left.position = dataset.position.shift()
                                self.context.final[packs.left.index] = packs.left
                            else:
                                packs.right.position = dataset.position.shift()
                                self.context.final[packs.right.index] = packs.right
                        else:
                            packs.right.position = dataset.position.shift()
                            self.context.final[packs.right.index] = packs.right
            except IndexError: ...


        """for data in dataset.action.copy().prepend(None):
            if window.append(data).length < 2: continue
            
            prev, this = window

            # 'bundle.action'
            package:bundle = bundle(action=this)

            # 'bundle.position'
            matched:array[str, ...] = dataset.position.filter(lambda mdata:
                (mdata.pos < this.pos)
                    if prev is None else
                (prev.pos < mdata.pos < this.pos)            
            )
            if matched.length: package.position = matched.pop()

            self.context.final.append(package)

        for data in dataset.value:
            
            # 'bundle.value'
            target = None
            for index, package in enumerate(self.context.final):
                if package.action.pos > data.pos: break
                if package.value is None: target = index
            if target is not None: ..."""
            


            

class Movements:

    @classmethod
    def read(cls, context:str):
        context = Context(context)
        source = context.context.source
        metadata = context.context.metadata
        final = context.context.final
        console.debug(source)
        console.debug(metadata)
        console.debug(final)