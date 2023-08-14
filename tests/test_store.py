# standard imports
import unittest
import logging

# local imports
from shep.persist import PersistedState
from shep.error import (
        StateExists,
        StateItemExists,
        StateInvalid,
        StateItemNotFound,
        )

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()


class MockStore:

    def __init__(self):
        self.v = {}
        self.for_state = 0


    def put(self, k, contents=None):
        self.v[k] = contents


    def remove(self, k):
        del self.v[k]


    def get(self, k):
        return self.v[k]


    def list(self):
        return list(self.v.keys())


class TestStateItems(unittest.TestCase):
        
    def setUp(self):
        self.mockstore = MockStore()

        def mockstore_factory(v):
            #self.mockstore.for_state = v
            return self.mockstore

        self.states = PersistedState(mockstore_factory, 4)
        self.states.add('foo') 
        self.states.add('bar') 
        self.states.add('baz') 
        self.states.alias('xyzzy', self.states.BAZ | self.states.BAR) 
        self.states.alias('plugh', self.states.FOO | self.states.BAR) 


    def test_persist_new(self):
        item = b'foo'
        self.states.put(item, True)
        self.assertTrue(self.mockstore.v.get(item))


    def test_persist_move(self):
        item = b'foo'
        self.states.put(item, self.states.FOO)
        self.states.move(item, self.states.XYZZY) 
        self.assertEqual(self.mockstore.for_state, self.states.name(self.states.XYZZY))


    def test_persist_move(self):
        item = b'foo'
        self.states.put(item, self.states.FOO, True)
        self.states.move(item, self.states.XYZZY) 
        #self.assertEqual(self.mockstore.for_state, self.states.name(self.states.XYZZY))
        # TODO: cant check the add because remove happens after remove, need better mock
        self.assertIsNone(self.mockstore.v.get(item)) 


    def test_persist_move_new(self):
        item = b'foo'
        self.states.put(item)
        self.states.move(item, self.states.BAZ)
        #self.assertEqual(self.mockstore.for_state, self.states.name(self.states.BAZ))
        self.assertIsNone(self.mockstore.v.get(item))



if __name__ == '__main__':
    unittest.main()
