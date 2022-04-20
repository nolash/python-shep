# standard imports
import unittest
import os
import logging
import sys
import importlib

# local imports
from shep.persist import PersistedState
from shep.error import (
        StateExists,
        StateInvalid,
        StateItemExists,
        StateItemNotFound,
        )

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()


class TestRedisStore(unittest.TestCase):
        
    def setUp(self):
        from shep.store.redis import RedisStoreFactory
        self.factory = RedisStoreFactory()
        self.factory.redis.flushall()
        self.states = PersistedState(self.factory.add, 3)
        self.states.add('foo') 
        self.states.add('bar') 
        self.states.add('baz') 


    def test_add(self):
        self.states.put('abcd', state=self.states.FOO, contents='baz')
        v = self.states.get('abcd')
        self.assertEqual(v, 'baz')
        v = self.states.state('abcd')
        self.assertEqual(v, self.states.FOO)


    def test_next(self):
        self.states.put('abcd')

        self.states.next('abcd')
        self.assertEqual(self.states.state('abcd'), self.states.FOO)
        
        self.states.next('abcd')
        self.assertEqual(self.states.state('abcd'), self.states.BAR)

        self.states.next('abcd')
        self.assertEqual(self.states.state('abcd'), self.states.BAZ)

        with self.assertRaises(StateInvalid):
            self.states.next('abcd')

        v = self.states.state('abcd')
        self.assertEqual(v, self.states.BAZ)


    def test_replace(self):
        with self.assertRaises(StateItemNotFound):
            self.states.replace('abcd', contents='foo')

        self.states.put('abcd', state=self.states.FOO, contents='baz')
        self.states.replace('abcd', contents='bar')
        v = self.states.get('abcd')
        self.assertEqual(v, 'bar')


    def test_factory_ls(self):
        r = self.factory.ls()
        self.assertEqual(len(r), 0)

        self.states.put('abcd')
        self.states.put('xxxx', state=self.states.BAZ)
        r = self.factory.ls()
        self.assertEqual(len(r), 2)

        self.states.put('yyyy', state=self.states.BAZ)
        r = self.factory.ls()
        self.assertEqual(len(r), 2)

        self.states.put('zzzz', state=self.states.BAR)
        r = self.factory.ls()
        self.assertEqual(len(r), 3)


if __name__ == '__main__':
    noredis = False
    redis = None
    try:
        redis = importlib.import_module('redis')
    except ModuleNotFoundError:
        logg.critical('redis module not available, skipping tests.')
        sys.exit(0)

    host = os.environ.get('REDIS_HOST', 'localhost')
    port = os.environ.get('REDIS_PORT', 6379)
    port = int(port)
    db = os.environ.get('REDIS_DB', 0)
    db = int(db)
    r = redis.Redis(host=host, port=port, db=db)
    try:
        r.get('foo')
    except redis.exceptions.ConnectionError:
        logg.critical('could not connect to redis, skipping tests.')
        sys.exit(0)
    except redis.exceptions.InvalidResponse as e:
        logg.critical('is that really redis running on {}:{}? Got unexpected response: {}'.format(host, port, e))
        sys.exit(0)

    unittest.main()
