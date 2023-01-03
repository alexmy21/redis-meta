import os
import string
import re
import pathlib
import sys
import meta.utils as utl
from meta.client import Client
from meta.commands import Commands as cmd
from meta.vocabulary import Vocabulary as voc
from pathlib import Path

client = Client()
client.create_index(voc.SCHEMAS, voc.DIR)
client.create_index(voc.SCHEMAS, voc.FILE)

rs = utl.getRedis(client.config_props)

def run(dir: dict|None):
    ret = {}
    if dir != None:
        directory = dir.get('dir')
    d_ret = dir_meta('dir_meta', 'meta', '', directory)
    # print(d_ret)
    ret[d_ret.get(voc.ID)] =  d_ret.get(voc.LABEL)
    for file in Path(directory).glob("**/*.csv"):
        # print('HEADER: {}'.format(utl.csvHeader(file)))
        f_ret = file_meta('file_meta', 'file_meta', d_ret, file)
        if f_ret == None:
            print('Error updating: {}'.format(file))
        else:
            ret[f_ret.get(voc.ID)] = f_ret.get(voc.LABEL)
    # print(os.path.dirname(__file__))
    return ret

'''
    dir_meta and file_meta are functions of source processors. Normally, processor should not take care about managing 
    "transaction" index, this is Controller responsibility. Source processors are exception of this rule. They populate 
    "transaction" index to be used  by other processors.
    redis-mds should provide source processors for most of data sources like files, data bases (relational and non relational), 
    documents , images, video, audio and other streaming data sources.
'''
def dir_meta(proc_id: str, proc_pref: str, parent_id: str, dir: str) -> dict|None:
    map = {
        voc.PARENT_ID: f'{parent_id}',
        voc.URL: f'{dir}',
        voc.LABEL: voc.DIR.upper(),
        voc.DOC: ''
    }
    _map: dict = Client.update_record(client, schema_dir=voc.SCHEMAS, schema_name=voc.DIR, map=map) 
    
    if cmd.txUpdate(rs, proc_id, proc_pref, _map[voc.ID], _map[voc.ITEM_PREFIX], voc.DIR, voc.WAITING) == None:
        return None
    else:
        return _map        

def file_meta(proc_id: str, proc_pref: str, dir: dict, file: str) -> dict|None:
    stats = os.stat(file)
    map = {
        voc.PARENT_ID: f'{dir.get(voc.ID)}',
        voc.URL: f'{file}',
        voc.LABEL: voc.FILE.upper(),
        voc.FILE_TYPE: utl.replaceChars(pathlib.Path(file).suffix),
        voc.SIZE: stats.st_size,
        voc.DOC: ''
    }
    _map: dict = Client.update_record(client, schema_dir=voc.SCHEMAS, schema_name=voc.FILE, map=map) 
    
    if cmd.txUpdate(rs, proc_id, proc_pref, _map[voc.ID], _map[voc.ITEM_PREFIX], _map[voc.FILE_TYPE], voc.WAITING) == None:
        return None
    else:
        return _map        

if __name__ == "__main__":
    if sys.argv.count == 2:
        globals()[sys.argv[1] ](sys.argv[2])
    else:
        print('Requeres 2 arguments.')
