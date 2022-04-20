# standard imports
import unittest
import os
import logging
import sys
import importlib
import tempfile
import shutil

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
        from shep.store.rocksdb import RocksDbStoreFactory
        self.d = tempfile.mkdtemp()
        self.factory = RocksDbStoreFactory(self.d)
        self.states = PersistedState(self.factory.add, 3)
        self.states.add('foo') 
        self.states.add('bar') 
        self.states.add('baz') 


    def tearDown(self):
        shutil.rmtree(self.d)


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
    norocksdb = False
    rocksdb = None
    try:
        importlib.import_module('rocksdb')
    except ModuleNotFoundError:
        logg.critical('rocksdb module not available, skipping tests.')
        sys.exit(0)

    unittest.main()
