import os
import pathlib
import redis as srv
from redis.commands.search.query import NumericFilter, Query

import meta.utils as utl
from . vocabulary import Vocabulary as voc

from . commands import Commands as cmd

class Client: 
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not Client.__instance:
            Client.__instance = object.__new__(cls)
        return Client.__instance 
    
    def __init__(self, _mds_home: str|None = None ):

        # print(os.path.normpath(os.path.exists(os.path.join(os.path.dirname(__file__), '.mds_py'))))

        if _mds_home is not None:
            if _mds_home in os.environ:
                self.mds_home = os.environ.get(_mds_home) 
            elif os.path.exists(_mds_home):
                self.mds_home = _mds_home
            else:
                self.mds_home = None
                raise RuntimeError(f"Error: Provided '{_mds_home}' mds home directory doesn't exist.")        
        elif voc.MDS_PY in os.environ:
            self.mds_home = os.environ.get(voc.MDS_PY)
        # .mds_py inside mds_py directory (??)
        # elif os.path.exists(os.path.join(os.path.dirname(__file__), '.mds_py')):
        #     self.mds_home = os.path.join(os.path.dirname(__file__), '.mds_py')
        else:
            self.mds_home = None
            raise RuntimeError(f"Error: Provided '{_mds_home}' mds home directory doesn't exist.")

         # set path for all standard directories in mds_home
        self.boot = os.path.join(self.mds_home, voc.BOOTSTRAP)
        self.config = os.path.join(self.mds_home, voc.CONFIG)
        self.processors = os.path.join(self.mds_home, voc.PROCESSORS)
        self.schemas = os.path.join(self.mds_home, voc.SCHEMAS)
        self.scripts = os.path.join(self.mds_home, voc.SCRIPTS)
        self.sqlite_files = os.path.join(self.mds_home, voc.SQLITE_FILES)
        
        path = os.path.join(self.mds_home, voc.CONFIG, utl.idxFileWithExt(voc.CONFIG_FILE)) 
        self.config_props = utl.getConfig(path) 

        Client.bootstrap(self)
    
    @staticmethod
    def bootstrap(self):
        rs = utl.getRedis(self.config_props)
        '''First create idx_reg index'''
        schema_path = os.path.join(self.mds_home, voc.BOOTSTRAP, utl.idxFileWithExt(voc.IDX_REG))
        cmd.createIndex(rs, voc.IDX_REG, self.mds_home, schema_path)
        '''
        get idx files from bootstrap directory
        and register them in idx_reg index
        all including idx_rg index itself 
        '''
        fileList = utl.fileList(self.boot)
        # print('Boot List: \n {}'.format(fileList))

        # rs: redis.Redis, mds_home:str, dir: str, fileList: list, register: bool
        cmd.createIndices(rs, self.mds_home, self.boot, fileList)

        procList = utl.fileList(self.processors)
        # print('Processors List: \n {}'.format(procList))

        # rs: redis.Redis, mds_home:str, dir: str, fileList: list, register: bool
        cmd.createIndices(rs, self.mds_home, self.processors, procList, True)

    # Following is a list  wrappers for commands from Commands module
    #====================================================================
    def schema_file_name(self, schema_dir: str, schema_name: str) -> str|None:
        return os.path.join(self.mds_home, schema_dir, utl.idxFileWithExt(schema_name))

    def schema_from_file(self, file_name: str) -> str|None:
        return utl.getSchemaFromFile(file_name)

    def index_info(self, idx_name: str) -> str|None:
        rs = utl.getRedis(self.config_props)
        return rs.ft(idx_name).info()

    def create_index(self, schema_dir: str, idx_name: str, proc: bool = False) -> str|None :
        rs = utl.getRedis(self.config_props)
        path = os.path.join(self.mds_home, schema_dir, utl.idxFileWithExt(idx_name))
        ret_str = cmd.createIndex(rs, idx_name, self.mds_home, path, proc)

        return ret_str
    
    @staticmethod
    def update_record(self, schema_dir: str, schema_name: str, map: dict) -> str|None:
        rs = utl.getRedis(self.config_props)
        path = os.path.join(self.mds_home, schema_dir, utl.idxFileWithExt(schema_name))
        # rs:redis.Redis, pref: str, idx_name: str, schema_path: str, map:dict
        # rs:redis.Redis, pref: str, schema_path: str, map:dict
        return cmd.updateRecord(rs, schema_name, path, map)

    def search(self, idx: str, query: str|Query, query_params: dict|None = None):
        rs = utl.getRedis(self.config_props)            
        return cmd.search(rs, idx, query)

    # rs: redis.Redis, index: str, query: str|Query, query_params: dict|None = None 
    def tx_lock(self, proc_id: str, query: str, batch: int = 100):
        rs = utl.getRedis(self.config_props) 
        limit = {
            'limit': batch
        }
        return cmd.search(rs, voc.TRANSACTION, query, limit)

    # rs: redis.Redis, proc_id: str, proc_pref: str, item_id: str, item_prefix: str, status: str
    def tx_status(self, proc_id: str, proc_pref: str, item_id: str, item_prefix: str, status: str) -> str|None:
        rs = utl.getRedis(self.config_props)
        return cmd.txStatus(rs, proc_id, proc_pref, item_id, status)

    
    print('=================== Client new instance =============================')