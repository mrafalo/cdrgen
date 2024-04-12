import os

if os.path.exists("C:/Program Files/NVIDIA/CUDA/v11.8/bin"):
    os.add_dll_directory("C:/Program Files/NVIDIA/CUDA/v11.8/bin")

if os.path.exists("C:/Program Files/NVIDIA/CUDNN/v8.6.0/bin"):
    os.add_dll_directory("C:/Program Files/NVIDIA/CUDNN/v8.6.0/bin")


import work.cdrgenerator as cdr
import work
import importlib


def main_loop():    
    cdr.run_generator()


main_loop()

# importlib.reload(work.cdrgenerator)

