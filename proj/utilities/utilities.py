import math
import time
import tracemalloc
import os
import psutil
from functools import wraps

from fastapi import Request, HTTPException

fernet_key = b'MBeEfw73JYBGiTpu-SZVj0bL55Ozoi1TNyS-HLqxIhg='


def logged(function):
    @wraps(function)
    async def wrapper(request: Request, *args, **kwargs):
        headers = request.headers.get('Authorization')
        if not headers:
            raise HTTPException(400)
        return await function(request, *args, **kwargs)

    return wrapper


def time_measurement_aspect(function):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        return_value = function(*args, **kwargs)
        end_time = time.time()
        print('Function {} {} lasted {} seconds'.format(function.__name__, [i for i in args[1:]] or [],
                                                        end_time - start_time))
        return return_value

    return wrapper


# the memory the code is currently using and the maximum space the program used while executing
def resource_measurement_aspect(function):
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        result = function(*args, **kwargs)
        traced_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        print("The memory the function is currently using: ", traced_memory[0])
        print("The maximum space the function used while executing: ", traced_memory[1])
        return result

    return wrapper


# inner psutil function
def process_memory():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss


# decorator function
def consumed_memory(func):
    def wrapper(*args, **kwargs):
        mem_before = process_memory()
        result = func(*args, **kwargs)
        mem_after = process_memory()
        print("{}:consumed memory: {:,} bytes\n".format(
            func.__name__,
            mem_before, mem_after, mem_after - mem_before))

        return result

    return wrapper


def get_string_from_vec(vec):
    s = ""
    for element in vec:
        s += str(element)
    return s


def get_vec_from_str(string_):
    vec = []
    for ch in string_:
        vec.append(int(ch))
    return vec