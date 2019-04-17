# __Redis Proxy Challenge (Segment)__: *James Groeneveld*
A super simple in-memory

## __High-level architecture overview__
### Components
1. [__client:__] the client can talk to the Proxy web service over HTTP -- this is left for the user.

1. __proxy:__ the Proxy web service talks with the Redis service over HTTP. This is a containerized Flask application using Gunicorn as the WSGI to handle concurrency. For the purposes of this assignment we set only a single worker and cap the number of threads at `2 * num_cores` on the proxy container. We spawn only a single worker process to ensure consistency with our __RedisCache__, otherwise we would have an instance of __RedisCache__ inside each worker process.

   __RedisCache:__ the Proxy web service offloads most of the heavy lifting onto this implementation of a RedisCache. It is an LRU Cache implementation with per-item time-to-live (TTL) setting based on [cachetools](https://github.com/tkem/cachetools/blob/master/cachetools/ttl.py) package. We have overridden the \__missing__ method to perform a roundtrip to our Redis backing instance if key is not currently in cache.

1. __e2e:__ a standalone end-to-end testing container as called out in requirements. Returns non-zero exit code if tests fail. If I had enough time I would have liked to write some unittests for my RedisCache subclass of [TTLCache](https://github.com/tkem/cachetools/blob/master/cachetools/ttl.py). The original author has decent [test coverage](https://github.com/tkem/cachetools/tree/master/tests) so we should be OK for now.

1. __redis:__ vanilla containerized Redis -- `redis:latest`.

### Configuration
Our configuration is set in [.env](.env).

* __REDIS_PORT__ (integer)

   [__required__]  
   default: 6379  
   A valid port number `1 <= REDIS_PORT <= 65535` for the host container mapping to the Redis container.


 * __PROXY_PORT__ (integer)

    [__required__]  
    default: 5000  
    A valid port number `1 <= PROXY_PORT <= 65535` for the host container mapping to the Proxy web service container.	 

* __CACHE_TTL__ (integer)

   [__optional__]  
	 default: 3600  
	 Per-item ttl setting in our __RedisCache__

* __CACHE_MAXSIZE__ (integer)

   [__optional__]  
   default: 1024  
   Fixed key size setting for our __RedisCache__

* __MAX_PARALLEL__ (integer)

   [__optional__]  
   default: 1  
   Set to 1 for _sequential concurrent processing_ otherwise > 1 for _parallel concurrent processing_. For safety we cap this setting with [max_threads](proxy/gunicorn.py:6).

* __MAX_CONNECTIONS__ (integer)

   [__optional__]  
   default: 2048  
   Maximum number of concurrent connections to our web service at any given time.


## What the code does
`./proxy/app.py`: Define the Flask application, instantiate an instance of __RedisCache__ and set the main route -- `/get/<key>`.  
`./proxy/Dockerfile`: Basic Dockerfile for Gunicorn backed Flask application.  
`./proxy/gunicorn.py`: Defines the Gunicorn WSGI configuration.  
`./proxy/redis_cache.py`: Extends the [cachetools](https://github.com/tkem/cachetools/blob/master/cachetools/ttl.py) based implementation of TTLCache but specifying custom behaviour when key is not in cache.  
`./.env`: single file for all configuration.  
`./docker-compose.yml`: Defines our Proxy and Redis components. No need to setup any special networking as the default network and communication between containers is sufficient.  
`Makefile`: defines `test` and `run`.

## Algorithmic complexity of the cache operations
__LRU__

Cachetools uses a dictionary mapping to a doubly linked list under the hood. Because deletion and insertion into a doubly linked list and dictionary are both __O(1)__ the complexity of the LRU implementation is as follows:

* __set:__ time -- O(1), space -- O(1)
* __get:__ time -- O(1), space -- O(1)
* __evict:__ time -- O(1), space -- O(1)


__TTL__

This implementation of TTL Cache will attempt to remove all expired keys on every state mutation. Because in the worst case we may need to expire all keys on any given mutation the complexity of the TTL implementation is as follows:

* __set:__ time -- O(n), space -- O(1)
* __get:__ time -- O(n), space -- O(1)
* __expire:__ time -- O(1), space -- O(1)

In practice, when we take TTL's `set` and `get` and amortize it over time we get an effective O(1) for each operation.


## Instructions for how to run the proxy and tests
__Run tests__  

    make test

__Run proxy (and redis)__

    make

## How long you spent on each part of the project

1. __documentation:__ 1hr

1. __proxy:__ 1.5hrs

1. __e2e:__ 1hr

1. __redis:__ n/a

1. __misc:__ 3hrs

   Spent reading about best practices (e.g. flask, docker, max_threads) and certain trade offs e.g. treating e2e testing as it's own service for extensibility, rather than setting an environment variable and running tests inside the application container.

## Unimplemented

* Some unit tests may have been helpful (inside the proxy service).  
* RESP protocol for proxy
