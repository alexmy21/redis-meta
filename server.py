import os
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from meta import utils as utl
from meta.vocabulary import Vocabulary as voc
from meta.controller import Controller

async def post_method(request):
    data: dict = await request.json() 
    path = os.path.dirname(__file__)

    match data.get(voc.LABEL):
        case 'SOURCE':
            print('SOURCE')
            _data: dict = Controller(path, data).source()
        case 'TRANSFORM':
            print('TRANSFORM')
            _data: dict = Controller(path, data).transform()
        case _:
            print('default case')

    return JSONResponse(_data)

def startup():
    print('Starlette started')

routes = [
    Route('/post', post_method, methods=['POST']),
]

app = Starlette(debug=True, routes=routes, on_startup=[startup])

# /home/alexmy/PYTHON/redis-mds/mds_py_app/file_meta.py