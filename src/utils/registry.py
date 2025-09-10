# backend_registry.py
import threading
import grpc
from itertools import cycle
from utils.redis_factory import init_redis
import json

class BackendRegistry:
    """Thread-safe registry mapping model_name -> cycle of (address, channel, stub) tuples, using Redis as storage."""
    _instances = {}
    _singleton_lock = threading.Lock()

    def __new__(cls, key):
        with cls._singleton_lock:
            if key not in cls._instances:
                instance = super().__new__(cls)
                cls._instances[key] = instance
            return cls._instances[key]

    def __init__(self, key):
        self.key = key
        self.r = init_redis()
        self._lock = threading.RLock()
        self._cycle_iters = {}

    def _redis_key(self, model_name):
        return f"{self.key}:{model_name}"

    def add_backend(self, model_name, address):
        with self._lock:
            key = self._redis_key(model_name)
            # Use Redis set to store addresses
            self.r.sadd(key, address)
            # Update the in-memory iterator
            addrs = list(self.r.smembers(key))
            addrs = [a.decode() if isinstance(a, bytes) else a for a in addrs]
            self._cycle_iters[model_name] = cycle(addrs)

    def remove_backend(self, model_name, address):
        with self._lock:
            key = self._redis_key(model_name)
            self.r.srem(key, address)
            addrs = list(self.r.smembers(key))
            addrs = [a.decode() if isinstance(a, bytes) else a for a in addrs]
            if not addrs:
                # Remove the key and iterator if no addresses left
                self.r.delete(key)
                self._cycle_iters.pop(model_name, None)
            else:
                self._cycle_iters[model_name] = cycle(addrs)

    def pick_backend(self, model_name):
        """Return (address, channel, stub) selected for model_name or None if none."""
        with self._lock:
            key = self._redis_key(model_name)
            addrs = list(self.r.smembers(key))
            addrs = [a.decode() if isinstance(a, bytes) else a for a in addrs]
            if not addrs:
                return None
            # get next address using the iterator
            it = self._cycle_iters.get(model_name)
            if it is None:
                it = cycle(addrs)
                self._cycle_iters[model_name] = it
            try:
                addr = next(it)
            except Exception:
                it = cycle(addrs)
                self._cycle_iters[model_name] = it
                addr = next(it)
            return addr

    def list_backends(self):
        with self._lock:
            # List all model_names by scanning Redis keys
            keys = self.r.keys(self._redis_key('*'))
            return keys
