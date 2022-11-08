import math
import time
import tracemalloc
import os
import psutil


def time_measurement_aspect(function):
	def wrapper(*args,**kwargs):
		start_time = round(time.time())
		return_value = function(*args,**kwargs)
		end_time = round(time.time())
		function_name = function.__name__
		print("Function \"",function_name, "\"(", *args, ") lasted", end_time - start_time, "s")
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
		print("{}:consumed memory: {:,} bytes".format(
			func.__name__,
			mem_before, mem_after, mem_after - mem_before))

		return result

	return wrapper
