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
    return JSONResponse(Controller(path, data).run())

def startup():
    print('Starlette started')

routes = [
    Route('/post', post_method, methods=['POST']),
]

app = Starlette(debug=True, routes=routes, on_startup=[startup])