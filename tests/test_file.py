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
        StateItemExists,
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
        with self.assertRaises(StateItemExists):
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


    def test_move(self):
        self.states.put('abcd', state=self.states.FOO, contents='foo')
        self.states.move('abcd', self.states.BAR)
        
        fp = os.path.join(self.d, 'BAR', 'abcd')
        f = open(fp, 'r')
        v = f.read()
        f.close()

        fp = os.path.join(self.d, 'FOO', 'abcd')
        with self.assertRaises(FileNotFoundError):
            os.stat(fp)
   
   
    def test_set(self):
        self.states.alias('xyzzy', self.states.FOO | self.states.BAR)
        self.states.put('abcd', state=self.states.FOO, contents='foo')
        self.states.set('abcd', self.states.BAR)

        fp = os.path.join(self.d, 'XYZZY', 'abcd')
        f = open(fp, 'r')
        v = f.read()
        f.close()

        fp = os.path.join(self.d, 'FOO', 'abcd')
        with self.assertRaises(FileNotFoundError):
            os.stat(fp)
    
        fp = os.path.join(self.d, 'BAR', 'abcd')
        with self.assertRaises(FileNotFoundError):
            os.stat(fp)

        self.states.unset('abcd', self.states.FOO)

        fp = os.path.join(self.d, 'BAR', 'abcd')
        f = open(fp, 'r')
        v = f.read()
        f.close()

        fp = os.path.join(self.d, 'FOO', 'abcd')
        with self.assertRaises(FileNotFoundError):
            os.stat(fp)
    
        fp = os.path.join(self.d, 'XYZZY', 'abcd')
        with self.assertRaises(FileNotFoundError):
            os.stat(fp)


    def test_sync(self):
        self.states.put('abcd', state=self.states.FOO, contents='foo')
        self.states.put('xxx', state=self.states.FOO)
        self.states.put('yyy', state=self.states.FOO)
       
        fp = os.path.join(self.d, 'FOO', 'yyy')
        f = open(fp, 'w')
        f.write('')
        f.close()

        fp = os.path.join(self.d, 'FOO', 'zzzz')
        f = open(fp, 'w')
        f.write('xyzzy')
        f.close()

        self.states.sync(self.states.FOO)
        self.assertEqual(self.states.get('yyy'), None)
        self.assertEqual(self.states.get('zzzz'), 'xyzzy')
        

if __name__ == '__main__':
    unittest.main()
