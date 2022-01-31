# standard imports
import unittest

# local imports
from schiz import State
from schiz.error import (
        StateExists,
        StateInvalid,
        )


class TestState(unittest.TestCase):

    def test_get(self):
        states = State(3)
        states.add('foo')
        states.add('bar')
        states.add('baz')
        self.assertEqual(states.BAZ, 4)


    def test_limit(self):
        states = State(2)
        states.add('foo')
        states.add('bar')
        with self.assertRaises(OverflowError):
            states.add('baz')


    def test_dup(self):
        states = State(2)
        states.add('foo')
        with self.assertRaises(StateExists):
            states.add('foo')


    def test_alias(self):
        states = State(2)
        states.add('foo')
        states.add('bar')
        states.alias('baz', states.FOO | states.BAR)
        self.assertEqual(states.BAZ, 3)


    def test_alias_limit(self):
        states = State(2)
        states.add('foo')
        states.add('bar')
        states.alias('baz', states.FOO | states.BAR)


    def test_alias_nopure(self):
        states = State(3)
        with self.assertRaises(ValueError):
            states.alias('foo', 4)


    def test_alias_cover(self):
        states = State(3)
        states.add('foo')
        states.add('bar')
        with self.assertRaises(StateInvalid):
            states.alias('baz', 5)



if __name__ == '__main__':
    unittest.main()
