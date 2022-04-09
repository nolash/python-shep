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


class TestFileStore(unittest.TestCase):
        
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.factory = SimpleFileStoreFactory(self.d)
        self.states = PersistedState(self.factory.add, 3)
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

        with self.assertRaises(StateItemExists): #FileExistsError):
            self.states.put('abcd', state=self.states.FOO)


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
   
  
    def test_change(self):
        self.states.alias('inky', self.states.FOO | self.states.BAR)
        self.states.put('abcd', state=self.states.FOO, contents='foo')
        self.states.change('abcd', self.states.BAR, 0)
        
        fp = os.path.join(self.d, 'INKY', 'abcd')
        f = open(fp, 'r')
        v = f.read()
        f.close()

        fp = os.path.join(self.d, 'FOO', 'abcd')
        with self.assertRaises(FileNotFoundError):
            os.stat(fp)

        fp = os.path.join(self.d, 'BAR', 'abcd')
        with self.assertRaises(FileNotFoundError):
            os.stat(fp)

        self.states.change('abcd', 0, self.states.BAR)

        fp = os.path.join(self.d, 'FOO', 'abcd')
        f = open(fp, 'r')
        v = f.read()
        f.close()

        fp = os.path.join(self.d, 'INKY', 'abcd')
        with self.assertRaises(FileNotFoundError):
            os.stat(fp)

        fp = os.path.join(self.d, 'BAR', 'abcd')
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


    def test_sync_one(self):
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


    def test_sync_all(self):
        self.states.put('abcd', state=self.states.FOO)
        self.states.put('xxx', state=self.states.BAR)

        fp = os.path.join(self.d, 'FOO', 'abcd')
        f = open(fp, 'w')
        f.write('foofoo')
        f.close()

        fp = os.path.join(self.d, 'BAR', 'zzzz')
        f = open(fp, 'w')
        f.write('barbar')
        f.close()

        self.states.sync()
        self.assertEqual(self.states.get('abcd'), None)
        self.assertEqual(self.states.get('zzzz'), 'barbar')


    def test_path(self):
        self.states.put('yyy', state=self.states.FOO)

        d = os.path.join(self.d, 'FOO')
        self.assertEqual(self.states.path(self.states.FOO), d)
        
        d = os.path.join(self.d, 'FOO', 'BAR')
        self.assertEqual(self.states.path(self.states.FOO, key='BAR'), d)


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

        fp = os.path.join(self.d, 'FOO', 'abcd')
        with self.assertRaises(FileNotFoundError):
            os.stat(fp)

        fp = os.path.join(self.d, 'BAZ', 'abcd')
        os.stat(fp)


    def test_replace(self):
        self.states.put('abcd')
        self.states.replace('abcd', 'foo')
        self.assertEqual(self.states.get('abcd'), 'foo')

        fp = os.path.join(self.d, 'NEW', 'abcd')
        f = open(fp, 'r')
        r = f.read()
        f.close()
        self.assertEqual(r, 'foo')


if __name__ == '__main__':
    unittest.main()
