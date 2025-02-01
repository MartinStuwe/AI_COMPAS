import mmap
import ctypes
import numpy as np
import os

# Load the C standard library
libc = ctypes.CDLL("libc.so.6")

# Constants for shared memory
O_RDWR = os.O_RDWR
shm_name1 = b"/compas_shared_memory"
size = 532*394

# Open the shared memory object
fd1 = libc.shm_open(shm_name1, O_RDWR, 0)
if fd1 < 0:
    raise OSError("Failed to open shared memory object")

# Map the shared memory object
mm = mmap.mmap(fd1, size)

# Function to get the shared memory content
# Surface Array
def get_shared_array_1():

    flat_array = np.frombuffer(mm[:size], dtype=np.uint8)
    reshaped_array = flat_array.reshape(532, 394)

    return reshaped_array

shm_name2 = b"/compas_shared_memory_player"
size2 = 4

# Open the shared memory object
fd2 = libc.shm_open(shm_name2, O_RDWR, 0)
if fd2 < 0:
    raise OSError("Failed to open shared memory object")

# Map the shared memory object
mm2 = mmap.mmap(fd2, size2)


shm_name3 = b"/compas_shared_memory_reference"
size3 = 16
fd3 = libc.shm_open(shm_name3, O_RDWR, 0)
if fd3 < 0 :
    raise OSError("Failed to open shared memory object")
mm3 = mmap.mmap(fd3, size3)

def get_shared_array_2():
    return np.frombuffer(mm2[:size2], dtype=np.int32)

def get_shared_object_3():
    return np.frombuffer(mm3[:size3], dtype=np.int32)

# Walls fehlt? Where? Currently communicated through shared memory shared_object_3. Due to reference point!