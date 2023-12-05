from toolbox import *
from sys import version_info
from enum import Enum
from collections import namedtuple
import random
class test(Enum):
    get = json({'alternative': [
    {'transcript': 'the snail smell like old Beer Mongers'}, 
    {'transcript': 'the still smell of old beer vendors'}, 
    {'transcript': 'the snail smell like old beer vendors'},
    {'transcript': 'the stale smell of old beer vendors'}, 
    {'transcript': 'the snail smell like old beermongers'}, 
    {'transcript': 'destihl smell of old beer vendors'}, 
    {'transcript': 'the still smell like old beer vendors'}, 
    {'transcript': 'bastille smell of old beer vendors'}, 
    {'transcript': 'the still smell like old beermongers'}, 
    {'transcript': 'the still smell of old beer venders'}, 
    {'transcript': 'the still smelling old beer vendors'}, 
    {'transcript': 'musty smell of old beer vendors'}, 
    {'transcript': 'the still smell of old beer vendor'}
    ], 'final': True})

    tester = get.alternative[1].transcript

    owo = 3
    uwu = 2
    qwq = 1

print(test.get.value, type(test.get.value))
print(test.tester.value, type(test.tester.value))

print(test.owo.value)
print(test.uwu)
print(test.qwq)

Gay = namedtuple('Gay', 'confirm')
fan = namedtuple('Sus', ['name', 'age', 'gender'])(name='Fanxiang', age=22, gender=Gay(confirm=True))

print(fan, type(fan))
print(fan.name)
print(fan.age)
print(fan.gender.confirm)

console.load(console.log, 'Hi')