from os import path
from json import loads, dumps

def read(scriptName, fileName):
    file = open(f'{path.join(path.dirname(scriptName), fileName)}.json', 'r')
    data = loads(file.read())
    file.close()
    return data

def write(scriptName, fileName, data):
    file = open(f'{path.join(path.dirname(scriptName), fileName)}.json', 'w')
    file.write(dumps(data, indent = 2))
    file.close()
