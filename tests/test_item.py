# standard imports
import unittest

# local imports
from shep import State
from shep.error import (
        StateExists,
        StateItemExists,
        StateInvalid,
        StateItemNotFound,
        )


class TestStateItems(unittest.TestCase):
        
    def setUp(self):
        self.states = State(4)
        self.states.add('foo') 
        self.states.add('bar') 
        self.states.add('baz') 
        self.states.alias('xyzzy', self.states.BAZ | self.states.BAR) 
        self.states.alias('plugh', self.states.FOO | self.states.BAR) 


    def test_put(self):
        item = b'foo'

        # put in initial (no) state
        self.states.put(item)

        with self.assertRaises(StateItemExists):
            self.states.put(item)

        with self.assertRaises(StateItemExists):
            self.states.put(item, self.states.BAZ)


    def test_item_state(self):
        item = b'foo'
        self.states.put(item, state=self.states.XYZZY)
        self.assertEqual(self.states.state(item), self.states.XYZZY)


    def test_item_move(self):
        item = b'foo'
        self.states.put(item, state=self.states.FOO)
        self.states.move(item, self.states.BAR)
        self.assertEqual(self.states.state(item), self.states.BAR)


    def test_item_move_from_alias(self):
        item = b'foo'
        self.states.put(item, state=self.states.FOO)
        self.states.move(item, self.states.XYZZY)
        self.assertEqual(self.states.state(item), self.states.XYZZY)
        self.states.move(item, self.states.BAR)
        self.assertEqual(self.states.state(item), self.states.BAR)


    def test_item_move_from_new(self):
        item = b'foo'
        self.states.put(item)
        self.assertEqual(self.states.state(item), self.states.NEW)
        self.states.move(item, self.states.XYZZY)
        self.assertEqual(self.states.state(item), self.states.XYZZY)


    def test_item_get(self):
        item = b'foo'
        self.states.put(item, state=self.states.BAZ, contents='bar')
        self.assertEqual(self.states.state(item), self.states.BAZ)
        v = self.states.get(item)
        self.assertEqual(v, 'bar')


    def test_item_set(self):
        item = b'foo'
        self.states.put(item, state=self.states.FOO)
        self.states.set(item, self.states.BAR)
        self.assertEqual(self.states.state(item), self.states.PLUGH)


    def test_item_set_invalid(self):
        item = b'foo'
        self.states.put(item, state=self.states.FOO)
        with self.assertRaises(StateInvalid):
            self.states.set(item, self.states.BAZ)

        item = b'bar'
        self.states.put(item, state=self.states.BAR)
        with self.assertRaises(ValueError):
            self.states.set(item, self.states.XYZZY)


    def test_item_set_invalid(self):
        item = b'foo'
        self.states.put(item, state=self.states.XYZZY)
        self.states.unset(item, self.states.BAZ)
        self.assertEqual(self.states.state(item), self.states.BAR)

        item = b'bar'
        self.states.put(item, self.states.XYZZY)
        with self.assertRaises(ValueError):
            self.states.unset(item, self.states.PLUGH)

        with self.assertRaises(ValueError):
            self.states.unset(item, self.states.FOO) # bit not set


if __name__ == '__main__':
    unittest.main()
