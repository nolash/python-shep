# standard imports
import unittest

# local imports
from shep import State
from shep.error import (
        StateExists,
        StateInvalid,
        )


class TestState(unittest.TestCase):

    def test_key_check(self):
        states = State(3)
        states.add('foo')

        for k in [
                'f0o',
                'f oo',
                'f_oo',
            ]:
            with self.assertRaises(ValueError):
                states.add(k)


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
            states.alias('foo', 1)
        states.add('foo')
        states.add('bar')
        states.alias('baz', states.FOO, states.BAR)
        self.assertEqual(states.BAZ, 3)


    def test_alias_multi(self):
        states = State(3)


    def test_alias_cover(self):
        states = State(3)
        states.add('foo')
        states.add('bar')
        with self.assertRaises(StateInvalid):
            states.alias('baz', 5)
    

    def test_peek(self):
        states = State(3)
        states.add('foo')
        states.add('bar')

        states.put('abcd')
        self.assertEqual(states.peek('abcd'), states.FOO)

        states.move('abcd', states.FOO)
        self.assertEqual(states.peek('abcd'), states.BAR)

        states.move('abcd', states.BAR)

        with self.assertRaises(StateInvalid):
            self.assertEqual(states.peek('abcd'))


    def test_from_name(self):
        states = State(3)
        states.add('foo')
        self.assertEqual(states.from_name('foo'), states.FOO)


if __name__ == '__main__':
    unittest.main()
