import redis

def run():
    r = redis.Redis(host='localhost', port=6379, db=0)

    # Reading script.lua file into a string
    f = open("/home/alexmy/PYTHON/redis-meta/meta-app/script.lua", "r")
    lua = f.read()

    new_list = [2,1,2]

    # Registering the script on the redis server
    operation:Script = r.register_script(lua)

    # Executing the script
    op_return = operation(keys=['mylist', 'sum'], args=new_list)

    print(op_return)

    return op_return