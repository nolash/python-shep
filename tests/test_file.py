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
        self.states.put('abcd', state=self.states.FOO, contents='baz')
        fp = os.path.join(self.d, 'FOO', 'abcd')
        f = open(fp, 'r')
        v = f.read()
        f.close()
        self.assertEqual(v, 'baz')


    def test_dup(self):
        self.states.put('abcd', state=self.states.FOO)
        with self.assertRaises(FileExistsError):
            self.states.put('abcd', state=self.states.FOO)

        with self.assertRaises(FileExistsError):
            self.states.put('abcd', state=self.states.FOO, force=True)

        self.states.put('abcd', contents='foo',  state=self.states.FOO, force=True)
        self.assertEqual(self.states.get('abcd'), 'foo')

        with self.assertRaises(FileExistsError):
            self.states.put('abcd', state=self.states.FOO, force=True)

        self.states.put('abcd', contents='bar',  state=self.states.FOO, force=True)
        self.assertEqual(self.states.get('abcd'), 'bar')


if __name__ == '__main__':
    unittest.main()
