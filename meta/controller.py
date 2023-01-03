import os
import redis
import importlib

from meta import utils as utl
from meta.vocabulary import Vocabulary as voc
from meta.client import Client 
from meta.commands import Commands as cmd

from redis.commands.search.query import Query
from redis.commands.search.result import Result

import polars as pl
# to enrich the examples in this quickstart with dates
from datetime import datetime, timedelta 
# to generate data for the examples
import numpy as np 


class Controller:
    
    def __init__(self, path:str, data:dict):
        self.path = path
        self.data = data

        self.uri = os.path.normpath(os.path.join(path, data.get(voc.PACKAGE), data.get(voc.NAME)))
        self.schema = data.get(voc.SCHEMA)
        module = '.' + data.get(voc.SCHEMA)
        package = data.get(voc.PACKAGE)
        self.processor = utl.importModule(module, package)        
        self.data = data

        host = Client().config_props.get(voc.REDIS, {}).get(voc.REDIS_HOST)
        port = Client().config_props.get(voc.REDIS, {}).get(voc.REDIS_PORT)
        self.rs = redis.Redis(host, port) 

        ''' 
            Update processor index
        '''
        path = os.path.join(Client().processors, data.get(voc.SCHEMA)) + '.yaml'
        # print('Controller: ' + path)
        cmd.updateRecord(self.rs, data.get(voc.SCHEMA), path, data.get(voc.PROPS))

    def run(self) -> dict|str|None:
        _data = {}
        _case = self.data.get(voc.LABEL)
        print(_case)
        match _case:
            case 'SOURCE':
                print('SOURCE')
                _data: dict = Controller(self.path, self.data).source()
            case 'TRANSFORM':
                print('TRANSFORM')
                _data: dict = Controller(self.path, self.data).process(voc.WAITING)
            case 'COMPLETE':
                print('COMPLETE')
                _data: dict = Controller(self.path, self.data).process(voc.COMPLETE)
            case 'TEST':
                print('TEST')
                _data: dict = Controller(self.path, self.data).test()
            case _:
                print('default case')

        return _data

    def source(self) -> dict|None:
        _data:dict = self.processor.run(self.data.get(voc.PROPS))
        return _data
    
    def process(self, status: str) -> dict|None:
        rs = utl.getRedis(Client().config_props) 
        _data:dict = self.data.get(voc.PROPS)
        resources = cmd.selectBatch(rs, voc.TRANSACTION, _data.get(voc.QUERY), _data.get(voc.LIMIT))
        dataframe =pl.DataFrame(resources.docs)
        print(dataframe) 
        ret = {}
        for doc in resources.docs:
            ret.update(self.processor.run(doc))
            _id = str(doc.id ).split(':')[1]
            cmd.txStatus(rs, self.schema, self.schema, _id, status)
        return ret
    
    def test(self) -> dict|None:
        _data:dict = self.processor.run()
        return _data

