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


    def test_list(self):
        self.states.put('abcd', state=self.states.FOO)
        self.states.put('xx!', state=self.states.FOO)
        self.states.put('1234', state=self.states.BAR)
        keys = self.states.list(self.states.FOO)
        self.assertIn('abcd', keys)
        self.assertIn('xx!', keys)
        self.assertNotIn('1234', keys)

        self.states.alias('xyzzy', self.states.BAR | self.states.FOO)
        self.states.put('yyy', state=self.states.XYZZY)

        keys = self.states.list(self.states.XYZZY)
        self.assertIn('yyy', keys)
        self.assertNotIn('1234', keys)
        self.assertNotIn('xx!', keys)
        

if __name__ == '__main__':
    unittest.main()
