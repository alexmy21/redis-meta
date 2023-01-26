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

On this diagram we have four types of metadata entities:

1. Business Ontology Entities;
2. Platform Ontology Entities;
3. Dictionary’s (catalog's) Entities;
4. Metadata Graph that represents different types of data-sets (instances of the metadata Entities).

Metadata management in this proposal is a schema driven. It means that all metadata entities are defined by schema. Schema is a metadata of the metadata entities, kind of meta-metadata.

Schema is yaml file created outside of the meta-app and located in the .mds_py directory. This directory holds information about all meta-metadata of the meta-app application.

Here is a list of main schema's categories:
- bootstrap - this is a collection of schemas that defines internal redis-meta metadata. This collection includes:
  - commit_tail schema. This is the schema of Redisearch index that holds commit history;
  - commit (or commit head) schema. This is the Redisearch index that holds current state of the all metadata indices;
  - idx_reg schema. It is a schema of the Redisearch index that holds metadata about all schemas;
  - prog_reg schema. It is a schema of the Redisearch index that holds metadata about all processors used in meta-app;
  - transaction schema. It is a schema of Redisearch index that is used to support processor orchestration;
- config - is a collection of configuration files;
- processors - this is collection of the schemas that describe processors used in meta-app;
- schemas - is a collection of user defined schemas for user specific data resources;
- scripts - collection of Lua scripts;
- sqlite_files - collection of SQLite files.

### Dictionaries, Bit sets, HLLs

These objects are persisted outside of the Metadata Graph. Depending on the meta-app implementation it could be:
- File System;
- Cloud storage, like AWS S3, minIO, and etc.;
- Distributed storage's like Hadoop;
- Relational or NoSql databases and so on.

### Redis Computational Engine

All metadata processing operations are using Redis data structures and Redis modules that provide support for:
- managing indices for entities and relations with Redisearch module;
- managing graph presentation of the Metadata using Redis Graph;
- performing Bit Set calculations using Redis roaring bit-set implementation;
- performing HLL calculations using built-in Redis HLL support.





