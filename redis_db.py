import logging
import os
import sys
import threading
import typing
from typing import Any

from redis import Redis as redis_base

log = logging.getLogger("telethon")

class RedisStr(redis_base):
    def __init__(
        self,
        host: str = None,
        port: int = None,
        password: str = None,
        logger=log,
        encoding: str = "utf-8",
        decode_responses: str = True,
        **kwargs,
    ):
        if ":" in host:
            data = host.split(":")
            host = data[0]
            port = int(data[1])
        if host.startswith("http"):
            logger.error("Your REDIS_URL should not start with http")
            sys.exit(1)
        elif not host or not port:
            logger.error("Port Number not found")
            sys.exit(1)
        kwargs["host"] = host
        if password and len(password) >= 1:
            kwargs["password"] = password
        kwargs["port"] = port
        kwargs["encoding"] = encoding
        kwargs["decode_responses"] = decode_responses
        try:
            super().__init__(**kwargs)
        except Exception as w:
            logger.exception(f"Error while connecting to redis: {w}")
            sys.exit(1)
        self.logger = logger
        self._cache = {}
        threading.Thread(target=self.re_cache).start()

    def re_cache(self):
        key = self.keys()
        for keys in key:
            self._cache[keys] = self.get(keys)
            self.logger.info("Cached {} keys".format(len(self._cache)))

    def get_key(self, key: Any):
        if key in self._cache:
            return self._cache[key]
        else:
            data = self.get(key)
            self._cache[key] = data
            return data

    def del_key(self, key: Any):
        if key in self._cache:
            del self._cache[key]
        return self.delete(key)

    def set_key(self, key: Any = None, value: Any = None):
        self._cache[key] = value
        return self.set(key, value)

# Render ke environment variable se URL uthayega
redis_host_url = os.getenv("REDIS_URL", "red-dalrvbid0e5s738eg8ag:6379")

db = RedisStr(
    host=redis_host_url,
    port=6379,
    password=None,
    decode_responses=True,
)

