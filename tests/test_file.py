# standard imports
import unittest
import tempfile
import os

# local imports
from shep.persist import PersistedState
from shep.store.file import SimpleFileStoreFactory
from shep.error import (
        StateExists,
        StateInvalid,
        )


class TestStateReport(unittest.TestCase):
        
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.factory = SimpleFileStoreFactory(self.d)
        self.states = PersistedState(self.factory.add, 4)
        self.states.add('foo') 
        self.states.add('bar') 
        self.states.add('baz') 


    def test_add(self):
        self.states.put('abcd', self.states.FOO)
        fp = os.path.join(self.d, 'FOO', 'abcd')
        f = open(fp, 'r')
        v = f.read()
        f.close()
        self.assertEqual(len(v), 0)


    def test_dup(self):
        self.states.put('abcd', self.states.FOO)
        with self.assertRaises(FileExistsError):
            self.states.put('abcd', self.states.FOO)
       

if __name__ == '__main__':
    unittest.main()
