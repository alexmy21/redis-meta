import os
import redis
import importlib

from meta import utils as utl
from meta.vocabulary import Vocabulary as voc
from meta.client import Client 
from meta.commands import Commands as cmd

from redis.commands.search.query import Query

class Controller:
    
    def __init__(self, path:str, data:dict):
        self.uri = os.path.normpath(os.path.join(path, data.get(voc.PACKAGE), data.get(voc.NAME)))
        module = '.' + data.get(voc.SCHEMA)
        package = data.get(voc.PACKAGE)
        self.processor = utl.importModule(module, package)        
        self.data = data

        host = Client().config_props.get(voc.REDIS, {}).get(voc.REDIS_HOST)
        port = Client().config_props.get(voc.REDIS, {}).get(voc.REDIS_PORT)
        self.rs = redis.Redis(host, port) 

        # Update processor index
        path = os.path.join(Client().processors, data.get(voc.SCHEMA)) + '.yaml'
        # print('Controller: ' + path)
        cmd.updateRecord(self.rs, data.get(voc.SCHEMA), path, data.get(voc.PROPS))

    def source(self) -> dict|None:
        _data:dict = self.processor.run(self.data.get(voc.PROPS))
        return _data

    def transform(self) -> dict|None:
        rs = utl.getRedis(Client().config_props) 
        _data:dict = self.data.get(voc.PROPS)
        query = '@processor_id: "file_meta" @status: "waiting"'
        resources = cmd.selectBatch(rs, voc.TRANSACTION, query, _data.get('limit'))
        # print('Transform resources: ', resources)
        ret = {}
        for doc in resources.docs:
            ret.update(self.processor.run(doc)) 
        return ret
