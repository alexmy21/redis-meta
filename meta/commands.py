import os
import redis
from redis.commands.search.field import TextField, NumericField, TagField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from redis.commands.search.result import Result
from redis.commands.search.document import Document

from . vocabulary import Vocabulary as voc
import meta.utils as utl
from cerberus import errors, Validator, SchemaError
import re

class Commands:

    @staticmethod
    def createIndex(rs: redis.Redis, idx_name: str, mds_home: str, schema_path: str, proc: bool = False) -> str|None: 
        sch = utl.getSchemaFromFile(schema_path)
        
        v = Validator()
        p_dict: dict = {}
        if v.validate(utl.doc_0, sch):
            n_doc = v.normalized(utl.doc_0, sch)
            p_dict = n_doc.get('props').items() 
        else:
            print('Inavalid: {}'.format(schema_path))
            return
        try:
            rs.ft(idx_name).create_index(utl.ft_schema(p_dict), definition=IndexDefinition(prefix=[utl.prefix(idx_name)]))
        except:
            # print('Index already exists')
            return
        finally:
            ''' 
                Register index even if it already exists. Just in case 
                if it was created on Redis server manualy
            '''
            if proc:
                Commands.registerProcessor(rs, mds_home, n_doc, sch)
            else:
                Commands.registerIndex(rs, mds_home, n_doc, sch)
        return 

    def createIndices(rs: redis.Redis, mds_home:str, dir: str, fileList: list, proc: bool = False):
        for file in fileList:
            idx_name = utl.schema_name(file)            
            path = os.path.join(mds_home, dir, file)
            Commands.createIndex(rs, idx_name, mds_home, path, proc)

    @staticmethod
    def registerIndex(rs: redis.Redis, mds_home: str, n_doc:dict, sch) -> dict|None:
        ''' Register index in idx_reg '''         
        file = os.path.join(mds_home, voc.BOOTSTRAP, voc.IDX_REG + '.yaml')
        idx_reg_dict: dict = {
            voc.NAME: n_doc.get(voc.NAME),
            voc.NAMESPACE: n_doc.get(voc.NAMESPACE),
            voc.PREFIX: n_doc.get(voc.PREFIX),
            voc.LABEL: n_doc.get(voc.LABEL),
            voc.KIND: n_doc.get(voc.KIND),
            voc.SOURCE: str(sch)
        }
        # print('IDX_REG record: {}'.format(idx_reg_dict[voc.LABEL]))
        return Commands.updateRecord(rs, voc.IDX_REG, file, idx_reg_dict)

    @staticmethod
    def registerProcessor(rs: redis.Redis, mds_home: str, n_doc:dict, sch) -> dict|None:
        ''' Register index in proc_reg '''         
        file = os.path.join(mds_home, voc.BOOTSTRAP, voc.PROC_REG + '.yaml')
        # print(file)
        proc_reg_dict: dict = {
            voc.LABEL: n_doc.get(voc.LABEL),
            voc.NAME: n_doc.get(voc.NAME),
            voc.VERSION: n_doc.get(voc.VERSION),
            voc.PACKAGE: n_doc.get(voc.PACKAGE),
            voc.LANGUAGE: n_doc.get(voc.LANGUAGE),
            voc.SCHEMA_DIR: n_doc.get(voc.SCHEMA_DIR),
            voc.SCHEMA: n_doc.get(voc.SCHEMA),
            voc.SOURCE: str(sch)
        }
        # print('IDX_REG record: {}'.format(idx_reg_dict[voc.LABEL]))
        return Commands.updateRecord(rs, voc.PROC_REG, file, proc_reg_dict)

    @staticmethod
    def updateRecord(rs:redis.Redis, pref: str, schema_path: str, map:dict) -> dict|None:
        _pref = utl.prefix(pref)        
        sch = utl.getSchemaFromFile(schema_path)     
        v = Validator()        
        k_list: dict = []
        id = ''
        if v.validate(utl.doc_0, sch):
            n_doc = v.normalized(utl.doc_0, sch)
            # print(n_doc)
            _map:dict = n_doc[voc.PROPS]
            _map.update(map)
            # print(_map)
            k_list = n_doc.get(voc.KEYS)
            id = utl.sha1(k_list, _map)
            _map[voc.ID] = id
            rs.hset(_pref + id, mapping=_map)
            # print('updateRecord: ', _pref + id,  _map)
            return _map
        else:
            print('updateRecord Error: ', _pref + id,  map)
            return None

    @staticmethod
    def getRecord(rs:redis.Redis, pref: str, item_id: str,) -> dict|None:
        return rs.hgetall(pref + item_id)

    def search(rs: redis.Redis, index: str, query: str|Query, query_params: dict|None = None) -> dict|None:
        _query: Query = Query(query).no_content(True).paging(0, 10)
        if query_params == None:
            result = rs.ft(index).search(query)
            doc: Document = result.docs[0]
            doc.id
            return result
        else:
            return rs.ft(index).search(query, query_params)            

    def selectBatch(rs:redis.Redis, idx_name: str, query:str, limit: int = 10) -> dict|None:
         _query = Query(query).no_content().paging(0, limit)

         return rs.ft(idx_name).search(_query)
    
    def txUpdate(rs: redis.Redis, proc_id: str, proc_pref: str, item_id: str, item_prefix: str, item_type: str, status: str) -> str|None:
        tx_pref = utl.prefix(voc.TRANSACTION)
        map:dict = rs.hgetall(tx_pref + item_id)
        _map = {}
        _map[voc.ID] = item_id
        _map[voc.PROCESSOR_ID] = proc_id
        _map[voc.PROCESSOR_PREFIX] = proc_pref
        _map[voc.ITEM_PREFIX] = item_prefix
        _map[utl.underScore(voc.ITEM_PREFIX)] = utl.underScore(item_prefix)
        _map[voc.ITEM_TYPE] = item_type
        _map[voc.PROCESSOR_UUID] = ' '
        _map[voc.STATUS] = status
        if map == None:
            _map[voc.ITEM_ID] = item_id
            _map[voc.ITEM_PREFIX] = item_prefix
            _map[voc.DOC] = ' '
            return rs.hset(tx_pref + item_id, mapping=_map)
        else:
            map.update(_map)
            return rs.hset(tx_pref + item_id, mapping=map)
        
    def txStatus(rs: redis.Redis, proc_id: str, proc_pref: str, item_id: str, status: str) -> dict|None:
        tx_pref = utl.prefix(voc.TRANSACTION)
        map:dict = rs.hgetall(tx_pref + ':' + item_id)        
        if map == None:
            return None
        else:            
            map[voc.PROCESSOR_ID] = proc_id
            map[voc.PROCESSOR_PREFIX] = proc_pref
            map[voc.STATUS] = status
            return rs.hset(tx_pref + item_id, mapping=map)

    def txLock(rs: redis.Redis, query:str, limit: int, uuid: str) -> str|None:

        return voc.OK

    def loadScripts(rs: redis.Redis, key: str, value: str) -> str|None:
        return rs.set(key, value)
