import sys
import meta.utils as utl
from meta.client import Client
from meta.vocabulary import Vocabulary as voc
from redis.commands.search.document import Document

client = Client()
client.create_index(voc.SCHEMAS, voc.DIR)
client.create_index(voc.SCHEMAS, voc.FILE)

rs = utl.getRedis(client.config_props)

'''
    This processor is taking record from transaction index with the reference to
    resources that it should process. In our case resource is a file that 
    file_ingest processor must process 
'''
def run(props: Document):
    print('col_ingest')
    ret = {}
    _id = props.id.split(':')
    ret[_id[1]] = _id[0]
    return ret

if __name__ == "__main__":
    if sys.argv.count == 2:
        globals()[sys.argv[1] ](sys.argv[2])
    else:
        print('Requeres 2 arguments.')
