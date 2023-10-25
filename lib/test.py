from toolbox import Gadget
from typing import Iterable
from time import time
from timeit import timeit
#people = [
#    {'name': 'Fan'},
#    {'name': 'Green'},
#    {'name': 'SCP'},
#    {'name': 'Carrie'},
#]
#print('\n'.join(map(str, (i['name'] for i in people))))
#print(list(map(lambda elem: elem['name'], people)))
arr = ('land', '3', '2')
arr2 = Gadget.formatter('takeoff,', split=',')

array = list()
array2 = list()

#match arr:
#    case str():
#        print('str!')
#    case int():
#        print('int!')
#    case float():
#        print('float!')
#    case bool():
#        print('bool!')
#    case list():
#        print('tuple!')
#    case tuple():
#        print('tuple2!')
#    case _:
#        print('something else!')

#array3 = type(arr)()

#print(array3, type(array3))
#print(type(tuple))


#a, = arr2
#print(a)
#text = "Fan is gay"
#print(
#    "Hi"'\n'
#    "Fan is gay"
#)
#
#print(arr2)

#arg = False
#def exec1():
#    if arg:
#        for _ in range(3): print(_, end=' ')
#
#def exec2():
#    for _ in range(3) if arg else (): print(_, end=' ')
#
#print(timeit("""
#def exec1():
#    if arg:
#        for _ in range(3): print(_, end=' ')
#"""))
#print(timeit("""
#def exec2():
#    for _ in range(3) if arg else (): print(_, end=' ')
#"""))

class test:
    data = 'Fan'
    _secret = 'is gay'

class new_test:
    def __init__(self, get):
        self.data = get.data
        self.other = get._secret

class another_test(test):
    ...

new = new_test(test)
another = another_test()
print(another.data)
print(another._secret)