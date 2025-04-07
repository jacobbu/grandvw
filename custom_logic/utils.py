import importlib

def load_logic(import_path):
    return importlib.import_module(import_path)
