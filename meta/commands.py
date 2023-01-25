import os
import redis
import duckdb
from redis.commands.search.indexDefinition import IndexDefinition
from redis.commands.search.query import Query
from redis.commands.search.document import Document

from . vocabulary import Vocabulary as voc
import meta.utils as utl
from cerberus import Validator

class Commands:

    # Playing with DuckDB
    def createDuckTable(db_name: str, schema_path: str, read_only: bool) -> str|None:
        sch = utl.getSchemaFromFile(schema_path)        
        p_dict, n_doc = utl.getProps(sch, schema_path) 
        conn = duckdb.connect(db_name, read_only = read_only)
        name = n_doc.get('name') 
        fields = ', '.join(f'{k} {v}' for k, v in p_dict)
        values = ', '.join(f'{utl.quotes(v)}' for k, v in p_dict)
        print(fields)
        print(values)
        conn.execute(f"CREATE TABLE {name}({fields})") 
        conn.execute(f"INSERT INTO {name} VALUES ({values})") 
        conn.execute(f"SELECT * FROM {name}")
        print(conn.fetchall())      

        return None

    @staticmethod
    def createIndex(rs: redis.Redis, idx_name: str, mds_home: str, schema_path: str, proc: bool = False) -> str|None: 
        sch = utl.getSchemaFromFile(schema_path)        
        p_dict, n_doc = utl.getProps(sch, schema_path)  

        if p_dict == None:
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
        return Commands.updateRecord(rs, voc.IDX_REG, file, idx_reg_dict, True)

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
        return Commands.updateRecord(rs, voc.PROC_REG, file, proc_reg_dict, True)

    '''
        Updates hash record or creates new if it doesn't exist
    '''
    @staticmethod
    def updateRecord(rs:redis.Redis, pref: str, schema_path: str, map:dict, in_idx: bool=False ) -> dict|None:
        '''
            Redisearch allows very simple implementation for a multistep transactional
            processing. 
            RS indecies based on hashes are linked to RS with the prefix that is
            a part of of index schema. 
            While we are working within a transaction we are using underscored prefix. This will keep
            record out of RS index.
            After commit we are renaming the record key (hash key) by removing underscore ('_')
            from the prefix. This brings record to the index. Kind of 'zero' copy solution :) 
            'in_idx' argument is a flag that indicates where record should be: in the index or outside,
            by default we keep record outside index.
        '''
        if in_idx:
            _pref = utl.prefix(pref) 
        else:
            _pref = utl.underScore(utl.prefix(pref)) 

        sch = utl.getSchemaFromFile(schema_path)     
        v = Validator()        
        k_list: dict = []
        id = ''
        if v.validate(utl.doc_0, sch):
            n_doc = v.normalized(utl.doc_0, sch)
            _map:dict = n_doc[voc.PROPS]
            _map.update(map)
            k_list = n_doc.get(voc.KEYS)
            id = utl.sha1(k_list, _map)
            _map[voc.ID] = id
            rs.hset(_pref + id, mapping=_map)
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
    
    # This is one of the methods that populates 'transaction' index 
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

    # Updates status od resource with the value that reflects the processing step  
    def txStatus(rs: redis.Redis, proc_id: str, proc_pref: str, item_id: str, status: str) -> dict|None:
        
        map:dict = rs.hgetall(item_id)        
        if map == None:
            return None
        else:            
            map[voc.PROCESSOR_ID] = proc_id
            map[voc.PROCESSOR_PREFIX] = proc_pref
            map[voc.STATUS] = status
            return rs.hset(item_id, mapping=map)

    # Work in progress, not finished yet
    def txLock(rs: redis.Redis, query:str, limit: int, uuid: str) -> str|None:

        return voc.OK

    # This supposes to load Lua scripts into Redis 
    def loadScripts(rs: redis.Redis, key: str, value: str) -> str|None:
        return rs.set(key, value)
