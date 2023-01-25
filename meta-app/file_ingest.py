import sys
import meta.utils as utl
from meta.client import Client
from meta.vocabulary import Vocabulary as voc
from redis.commands.search.document import Document
import polars as pl

import duckdb as duck

client = Client()
client.create_index(voc.SCHEMAS, voc.DIR)
client.create_index(voc.SCHEMAS, voc.FILE)

rs = utl.getRedis(client.config_props)

import csv

def get_delimiter(file_path, bytes = 4096):
    sniffer = csv.Sniffer()
    data = open(file_path, "r").read(bytes)
    delimiter = sniffer.sniff(data).delimiter
    return delimiter

'''
    This processor is taking record from transaction index with the reference to
    resources that it should process. In our case resource is a file that 
    file_ingest processor must process 
'''
def run(data: Document, duckdb_name: str|None = None) -> dict|None:
    rs = utl.getRedis(client.config_props)

    map:dict = rs.hgetall(data.id)
    
    _item_prefix = utl.underScore(map.get(voc.ITEM_PREFIX))
    hash_id = _item_prefix + ':' + data.id.split(':')[1]
    file_map:dict = rs.hgetall(hash_id)
    table_name = 't_' +data.id.split(':')[1]

    try:
        con = duck.connect(database=duckdb_name, read_only=False)
        
        query = f"CREATE TABLE {table_name} AS SELECT * FROM read_csv_auto('{file_map.get(voc.URL)}');"
        print(query)        
        con.begin()        
        con.execute(query)
        print(con.table(table_name).columns)
        print(con.table(table_name).dtypes)
        con.commit()
        con.close()  
        return {f"'{table_name}'" : f"'{hash_id}'"}     
    except:
        return {'error': 'duck db error'}


if __name__ == "__main__":
    if sys.argv.count == 2:
        globals()[sys.argv[1] ](sys.argv[2])
    else:
        print('Requeres 2 arguments.')
