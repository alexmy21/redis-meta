import os
from pathlib import Path
import redis
from meta.client import Client

def run():
    r = redis.Redis(host='localhost', port=6379, db=0)

    # Reading script.lua file into a string
    script_dir = Client().scripts

    print(script_dir)

    ret = {}
    for file in Path(script_dir).glob("**/*.lua"):
        file_name = os.path.basename(file).split('.')[0]
        _file = str(file)
        print(_file)
        print(file_name)
        f = open(file, "r")
        lua = f.read()
        sha = r.script_load(lua)
        ret[file_name] = sha

    print(ret)
    print(*ret)

    r.hset('lua_scripts', mapping = ret)
    print(r.hgetall('lua_scripts'))

    _sha = r.hget('lua_scripts', 'script')
    print(_sha)

    _ret = r.evalsha(_sha.decode(), 2, 'mylist', 'sum', 2, 1, 2)

    return _ret