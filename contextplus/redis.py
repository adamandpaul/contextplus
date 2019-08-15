# -*- coding:utf-8 -*-

from . import base
from .reify import reify
from typing import Iterable

import pickle


class DomainRedisNamespace(base.DomainBase):
    """A domain object which is backed by a redis namespace

    The use case for this kind of object is for structures which
    don't need to be permanent and can be recovered without
    significant data loss. Such as a login session or a
    shopping cart or a back ground process.

    Attributes:

        redis_keys (list): A list of key suffixes which are used in this
            object. This list is used in cases where redis_touch is called
            or there is a need to delete all objects

        redis_default_ex (int): An integer og seconds used for when objects
            are ejected from the cache.

        workflow_obj_key (str): The name of the key which will be used
            for workflow state
    """

    @reify
    def redis_namespace(self) -> str:
        """The namespace is used to prefix keys and and prevent conflicts"""
        meta_title = self.get_meta_title()
        return f"domain:{meta_title}:{self.name}"

    redis_keys = ["obj"]

    redis_default_ex = 60 * 60 * 24  # 24 hours

    def redis_touch(self):
        """Set or reset default expire on all the objects listed in redis_keys"""
        ns = self.redis_namespace
        ex = self.redis_default_ex
        pipe = self.acquire.redis.pipeline()
        pipe.hset(f"{ns}:obj", "_touch", 1)
        for key in self.redis_keys:
            pipe.expire(f"{ns}:{key}", ex)
        pipe.execute()

    def obj_dump(self, obj) -> bytes:
        """Serialise a python object into bytes for storage in the obj hash"""
        return pickle.dumps(obj)

    def obj_load(self, buf: bytes):
        """De-serialize bytes from the obj hash into a python object"""
        return pickle.loads(buf)

    def obj_set(self, key: str, value):
        """Set a key in the obj to the value"""
        buf = self.obj_dump(value)
        self.acquire.redis.hset(f"{self.redis_namespace}:obj", key, buf)

    def obj_get(self, key: str):
        """Retrieve an object stored in the obj hash at the key name"""
        buf = self.acquire.redis.hget(f"{self.redis_namespace}:obj", key)
        if isinstance(buf, bytes):
            return self.obj_load(buf)
        elif buf is None:
            return None
        else:
            raise Exception("Unexpected response type from redis")

    def obj_mget(self, *keys) -> Iterable:
        """Retrieve an object stored in the obj hash at the key name"""
        pipe = self.acquire.redis.pipeline()
        hash_key = f"{self.redis_namespace}:obj"
        for key in keys:
            pipe.hget(hash_key, key)
        for buf in pipe.execute():
            if buf is not None:
                yield self.obj_load(buf)
            else:
                yield None

    def obj_dict_get(self, *keys) -> dict:
        """Get a series of objs stored as a dictionary"""
        values = self.obj_mget(*keys)
        return dict(zip(keys, values))

    workflow_obj_key = "workflow_state"

    @reify
    def workflow_state(self) -> str:
        """Get the current workflow state stored in redis"""
        state = self.obj_get(self.workflow_obj_key)
        return state or self.workflow_default_state

    def workflow_set_state(self, state: str):
        """Set the current workflow state stored in redis"""
        self.obj_set(self.workflow_obj_key, state)
        self.workflow_state = state
