# redis-meta

is embeddable meta data discovery, extraction, collection, and management framework utilizing Redis, specifically Redisearch, Redis Graph, and very powerful computational capability of core Redis like HyperLogLog, Bloomfilter,Stream, etc.

## Installation

Tested on Linux (ubuntu 22.04). This project is in very begining stage of development, so be patient errors are the norm :)

1. Run git command:

`~/PYTHON/$ git clone https://github.com/alexmy21/redis-meta.git`

2. Create local virtual environment:

`~/PYTHON/$ python3 -m venv redis-meta`

3. Change directory to the redis-meta:

`~/PYTHON/$ cd redis-meta`

4. Activate venv:

`~/PYTHON/redis-meta$ source <path_to_redis-meta>/bin/activate`

5. Install all packages from requirements.txt file:

`~/PYTHON/redis-meta$ pip install -r requirements.txt `

6. Make .mds_py accessible from local environment:

`~/PYTHON/redis-meta$ export MDS_PY=<path_to_redis-meta>.mds_py`
