import csv
import importlib
import re
import string
from . vocabulary import Vocabulary as voc

import imp
import os

import os
import yaml
import redis
import hashlib

from redis.commands.search.field import TextField, NumericField, TagField
from redis.commands.search.query import NumericFilter, Query

from meta.commands import Commands as cmd


doc_0 = {'props': {}}

# def updateMeta(rs:redis.Redis, pref: str, schema_path: str, map:dict) -> str|None:
#     _map: dict = cmd.updateRecord(rs, pref, schema_path, map=map) 
#     if _map == None:
#         return None   
#     else:
#         st_map: dict = cmd.txUpdate(rs, proc_id, proc_pref, _map[voc.ID], _map[voc.ITEM_PREFIX], voc.DIR, voc.WAITING)
#         if st_map == None:
#             return None
#         else:
#             return _map[voc.ID]

def importModule(module: str, package: str):
    try:
        return importlib.import_module(module, package=package) 
    except ImportError as err:
        print('Error:', err)
        return None

def fileList(dir: str) -> list|None:
    return os.listdir(dir)

def getSchemaFromFile(file_name):     
    with open(file_name, 'r') as file:
        return yaml.safe_load(file)

def schema_name(file_name: str) -> str|None:
    return file_name.split('.')[0]

def idxFileWithExt(schema: str) -> str|None:
    if schema.endswith('.yaml'):
        return
    else:
        return schema + '.yaml' 

def getConfig(file_name: str|None) -> dict|None:
    config: dict | None
    try:
        with open(file_name, 'r') as file:
            config = yaml.safe_load(file)
    except:
        raise RuntimeError(f"Error: Problem with '{file_name}' file.")            
    return config
   
def getRedis(config: dict) -> redis.Redis|None:
    host = config.get(voc.REDIS, {}).get(voc.REDIS_HOST)
    port = config.get(voc.REDIS, {}).get(voc.REDIS_PORT)

    return redis.Redis(host, port)      

def ft_schema(schema: dict) -> tuple|None:
    dictlist = []
    tmp: str
    for key, value in schema:
        if value == 'tag':
            temp = TagField(key)
            dictlist.append(temp)
        elif value == 'numeric':
            temp = NumericField(key)
            dictlist.append(temp)
        else:
            temp = TextField(key)
            dictlist.append(temp) 
    return tuple(i for i in dictlist)

# Generates SHA1 hash code from key fields of props 
# dictionary
def sha1(keys: list, props: dict) -> str|None:
    sha = '' 
    for key in keys:
        # Normalize strings by turing to low case
        # and removing spaces
        if props.get(str(key)) != None:
            sha+= str(props.get(str(key))).lower().replace(' ', '')

    m = hashlib.sha1()
    m.update(sha.encode())
    return m.hexdigest()

'''
    Mics methods
'''

def prefix(term: str) -> str:
    if term.endswith(':'):
        return term
    else:
        return term + ':'

def underScore(term: str) -> str|None:
    if term.startswith('_'):
        return term
    else:
        return '_' + term

def csvHeader(file_path: str) -> bool|None:
    try:
        with open(file_path, mode = 'r', encoding="utf-8", errors="backslashreplace") as csvfile:
            return csv.Sniffer().has_header(csvfile.read(4096))
    except:
        print('Error reading file')
        return None

def replaceChars(text:str) -> str|None:
    chars = re.escape(string.punctuation)
    return re.sub(r'['+chars+']', '', text)