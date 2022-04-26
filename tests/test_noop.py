# standard imports
import unittest
import os
import logging
import sys
import importlib
import tempfile

# local imports
from shep.persist import PersistedState
from shep.store.noop import NoopStoreFactory
from shep.error import (
        StateExists,
        StateInvalid,
        StateItemExists,
        StateItemNotFound,
        )

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()


class TestNoopStore(unittest.TestCase):
        
    def setUp(self):
        self.factory = NoopStoreFactory()
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
        self.states.put('abcd')
        self.states.put('xxxx', state=self.states.BAZ)
        r = self.factory.ls()
        self.assertEqual(len(r), 0)


if __name__ == '__main__':
    unittest.main()
