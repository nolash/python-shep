# standard imports
import unittest

# local imports
from schiz import State
from schiz.error import StateExists


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


if __name__ == '__main__':
    unittest.main()
