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

    def __init__(self, context: str):

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

            def config(self, group: Literal['length', 'scale', 'time'] = ..., pos: int = ..., priority: int = ..., weight: int = ..., match: str = ..., category: Literal['position', 'action', 'value', 'unit'] = ...):
                # generic attributes
                if priority is not Ellipsis: self.priority = priority
                if weight is not Ellipsis: self.weight = weight
                if category is not Ellipsis: self.category = category
                if match is not Ellipsis: self.match = match

                # for action / unit only
                if group is not Ellipsis: self.group = group

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
                                try:
                                    assert not (info is None) # @IgnoreException
                                    assert not (len(info.match) < len(CHI)) # @IgnoreException
                                    assert not (info.priority < attr.priority) # @IgnoreException
                                except AssertionError:
                                    info = metadata(ENG).config(
                                        priority = attr.priority,
                                        weight = attr.weight,
                                        match = CHI,
                                        category = CTG
                                    )
                                    try:
                                        info.config(group=attr.group) # @IgnoreException
                                    finally:
                                        break

            return info

        for text in self.context.source:
            info = translator(text)
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
        for metadata in self.context.metadata:
            match metadata.category:
                case 'action': self.context.final.append(bundle(action=metadata, index=self.context.final.length))
                case 'position': dataset.position.append(metadata)
                case 'value': dataset.value.append(metadata)
                case 'unit': dataset.unit.append(metadata)
                case _: raise Exception(f'Unexpected Exception occurred caused by Context.context.metadata owns illegal category attribute: {metadata.category}')

        class window: ...
        class package: ...
        class scope: ...
        
        SIZE = 3
        window: slider = slider(size=SIZE)
        scope = ntuple('scope', ('left', 'right'))

        @dataclass
        class property_blueprint:
            position: object
            value: object

        for package in [None, *self.context.final, None]:

            if window.append(package).length < SIZE: continue
            
            def between(target: Literal['<object metadata>']) -> tuple:
                nonlocal prev, this, next
                if target is not None:
                    if prev is None:
                        if target.pos < next.action.pos:    
                            return scope(left=None, right=this) if target.pos < this.action.pos else scope(left=this, right=next)
                    elif next is None:
                        if prev.action.pos < target.pos:
                            return scope(left=this, right=None) if this.action.pos < target.pos else scope(left=prev, right=this)
                    elif prev.action.pos < target.pos < next.action.pos:
                        return scope(left=prev, right=this) if target.pos < this.action.pos else scope(left=this, right=next)
                    
                return None
            
            def headElement(source: array) -> Literal['<object metadata>']:
                try: return source[0] # @IgnoreException
                except IndexError: return None

            def modify_position(obj: Literal['<object metadata>']):
                obj.position = dataset.position.shift()

            def modify_value(obj: Literal['<object metadata>']):
                nonlocal suffix

                obj.value = dataset.value.shift()

                try: assert suffix.group == obj.action.group # @IgnoreException

                except (AttributeError, AssertionError):
                    match obj.action.group:
                        case 'length': obj.unit = 'cm'
                        case 'scale': obj.unit = 'deg'
                        case 'time': obj.unit = 'sec'

                else: obj.unit = suffix

            prev, this, next = window

            target = property_blueprint(
                position = headElement(dataset.position),
                value = headElement(dataset.value),
            )
            bound = property_blueprint(
                position = between(target.position),
                value = between(target.value),
            )
            modify = property_blueprint(
                position = modify_position,
                value = modify_value
            )

            # 'position'
            if bound.position:
                if bound.position.left is None or bound.position.right is None:
                    modify.position(this)
                else:
                    if bound.position.left.position is None:
                        dist = scope(
                            left = abs(target.position.pos - bound.position.left.action.pos),
                            right = abs(target.position.pos - bound.position.right.action.pos)
                        )
                        # 距離相同，右側優先
                        if dist.left < dist.right:
                            modify.position(bound.position.left)
                        else:
                            modify.position(bound.position.right)
                    else:
                        modify.position(bound.position.right)

            try: # expected to fetch 'unit' metadata
                suffix = self.context.metadata[target.value.pos + 1] # @IgnoreException
                assert suffix.category.__eq__('unit') # @IgnoreException
            except (IndexError, AssertionError, AttributeError):
                suffix = None
            
            # 'value / unit'
            if bound.value:
                
                if bound.value.left is None or bound.value.right is None:
                    modify.value(this)
                else:
                    if bound.value.left.value is None:
                        try:
                            # 有unix -> unix 符合的優先
                            if suffix is not None:
                                match = scope(
                                    left = bound.value.left.action.group == suffix.group,
                                    right = bound.value.right.action.group == suffix.group
                                )
                                assert not (match.left and not match.right), 'left' # @IgnoreException
                                assert not (match.right and not match.left), 'right' # @IgnoreException
                                assert not (not match.left and not match.right), 'left' # @IgnoreException

                            # unix 都一樣 / 找不到 unix -> 看 weight (left first)
                            # 數值在前面的 action 應該把 weight 設最高（目前 5）
                            assert not (bound.value.left.action.weight >= bound.value.right.action.weight), 'left' # @IgnoreException
                            assert not (bound.value.left.action.weight < bound.value.right.action.weight), 'right' # @IgnoreException


                        except AssertionError as AE:
                            match str(AE):
                                case 'left': modify.value(bound.value.left)
                                case 'right': modify.value(bound.value.right)
                    else:
                        modify.value(bound.value.right)

            

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
        for bundle in final: console.viewer(obj=bundle)