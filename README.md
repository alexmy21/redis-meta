# redis-meta

is embeddable meta data discovery, extraction, collection, and management framework utilizing Redis, specifically Redisearch, Redis Graph, and very powerful computational capability of core Redis like HyperLogLog, Bloomfilter, Streams, etc.

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

## Running project

There are two sub-projects in this repository:

1. meta - is a core embeddable python libraray;
2. meta-app - it is created to demo how redis-meta can be used in user's applications.

To run meta-app you should execute the following command from the terminal (assuming that you are in the project root and you activated venv):

`(redis-meta) alex:~/PYTHON/redis-meta$ uvicorn server:app --reload`

I am using postman to communicate with meta-app. You can find postman collection in the file

`redis-meta.postman_collection.json`

that is in root of the project.

![Screenshot from 2023-01-25 13-27-09](https://user-images.githubusercontent.com/1112548/214653070-49debd90-a486-4fab-8063-e37c53f4306f.png)


## Very short introduction into meta data

![image](https://user-images.githubusercontent.com/1112548/214657224-c294c0e4-bd77-4200-abc5-b7cf133fa716.png)




