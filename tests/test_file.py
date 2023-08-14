# standard imports
import unittest
import tempfile
import os
import shutil

# local imports
from shep.persist import PersistedState
from shep.store.file import SimpleFileStoreFactory
from shep.error import (
        StateExists,
        StateInvalid,
        StateItemExists,
        StateLockedKey,
        )


class TestFileStore(unittest.TestCase):
        
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.factory = SimpleFileStoreFactory(self.d)
        self.states = PersistedState(self.factory.add, 3)
        self.states.add('foo') 
        self.states.add('bar') 
        self.states.add('baz') 


    def tearDown(self):
        shutil.rmtree(self.d)


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

        fp = os.path.join(self.d, 'BAR', 'yyyy')
        f = open(fp, 'w')
        f.close()

        self.states.sync()
        self.assertEqual(self.states.get('abcd'), None)
        self.assertEqual(self.states.state('abcd'), self.states.FOO)
        self.assertEqual(self.states.get('zzzz'), 'barbar')
        self.assertEqual(self.states.state('zzzz'), self.states.BAR)
        self.assertEqual(self.states.get('yyyy'), None)
        self.assertEqual(self.states.state('yyyy'), self.states.BAR)


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


    def test_factory_ls(self):
        r = self.factory.ls()
        self.assertEqual(len(r), 4)

        self.states.put('abcd')
        self.states.put('xxxx', state=self.states.BAZ)
        r = self.factory.ls()
        self.assertEqual(len(r), 4)

        self.states.put('yyyy', state=self.states.BAZ)
        r = self.factory.ls()
        self.assertEqual(len(r), 4)

        self.states.put('zzzz', state=self.states.BAR)
        r = self.factory.ls()
        self.assertEqual(len(r), 4)


    def test_lock(self):
        factory = SimpleFileStoreFactory(self.d, use_lock=True)
        states = PersistedState(factory.add, 3)
        states.add('foo') 
        states.add('bar') 
        states.add('baz') 
        states.alias('xyzzy', states.FOO | states.BAR)
        states.alias('plugh', states.FOO | states.BAR | states.BAZ)
        states.put('abcd')

        lock_path = os.path.join(self.d, '.lock')
        os.stat(lock_path)

        fp = os.path.join(self.d, '.lock', 'xxxx')
        f = open(fp, 'w')
        f.close()
        
        with self.assertRaises(StateLockedKey):
            states.put('xxxx')

        os.unlink(fp)
        states.put('xxxx')

        states.set('xxxx', states.FOO)
        states.set('xxxx', states.BAR)
        states.replace('xxxx', contents='zzzz')

        fp = os.path.join(self.d, '.lock', 'xxxx')
        f = open(fp, 'w')
        f.close()

        with self.assertRaises(StateLockedKey):
            states.set('xxxx', states.BAZ)
        
        v = states.state('xxxx')
        self.assertEqual(v, states.XYZZY)

        with self.assertRaises(StateLockedKey):
            states.unset('xxxx', states.FOO)

        with self.assertRaises(StateLockedKey):
            states.replace('xxxx', contents='yyyy')

        v = states.get('xxxx')
        self.assertEqual(v, 'zzzz')


    def test_persist_set_same(self):
        item = 'abcd'
        self.states.alias('xyzzy', self.states.FOO, self.states.BAR)
        self.states.put(item)
        self.states.state(item)
        self.states.next(item)
        self.states.set(item, self.states.BAR)
        self.assertEqual(self.states.state(item), self.states.XYZZY)
      
        self.states.set(item, self.states.BAR)
        self.assertEqual(self.states.state(item), self.states.XYZZY)

        d = tempfile.mkdtemp()
        self.factory = SimpleFileStoreFactory(d)
        states = PersistedState(self.factory.add, 3, check_alias=False)
        item = 'abcd'
        states.add('foo') 
        states.add('bar') 
        states.add('baz') 
        states.put(item)
        states.state(item)
        states.next(item)
        states.set(item, self.states.BAR)
        self.assertEqual(states.state(item), states.FOO | states.BAR)
        self.assertEqual(states.state(item), states._FOO__BAR)


if __name__ == '__main__':
    unittest.main()
