from functools import wraps
from threading import Lock

def singleton(cls):
    instances = {}
    lock = Lock()
    @wraps(cls)
    def get_instance(*args, **kwargs):
        with lock:
            if cls not in instances:
                instances[cls] = cls(*args, **kwargs)
            return instances[cls]
    return get_instance