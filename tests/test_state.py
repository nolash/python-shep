# standard imports
import unittest
import logging

# local imports
from shep import State
from shep.error import (
        StateExists,
        StateInvalid,
        )

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()


class MockCallback:

    def __init__(self):
        self.items = {}


    def add(self, k, v):
        if self.items.get(k) == None:
            self.items[k] = []
        self.items[k].append(v)


class TestState(unittest.TestCase):

    def test_key_check(self):
        states = State(3)
        states.add('foo')

        for k in [
                'f0o',
                'f oo',
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
        states = State(3)
        states.add('foo')
        states.add('bar')
        states.add('baz')
        with self.assertRaises(OverflowError):
            states.add('gaz')


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


    def test_alias_invalid(self):
        states = State(3)
        states.add('foo')
        states.add('bar')
        states.put('abcd')
        states.set('abcd', states.FOO)
        with self.assertRaises(StateInvalid):
            states.set('abcd', states.BAR)


    def test_alias_invalid_ignore(self):
        states = State(3, check_alias=False)
        states.add('foo')
        states.add('bar')
        states.put('abcd')
        states.set('abcd', states.FOO)
        states.set('abcd', states.BAR)
        v = states.state('abcd')
        s = states.name(v)
        self.assertEqual(s, '*FOO,BAR')


    def test_peek(self):
        states = State(2)
        states.add('foo')
        states.add('bar')

        states.put('abcd')
        self.assertEqual(states.peek('abcd'), states.FOO)

        states.move('abcd', states.FOO)
        self.assertEqual(states.peek('abcd'), states.BAR)

        states.move('abcd', states.BAR)

        with self.assertRaises(StateInvalid):
            states.peek('abcd')


    def test_from_name(self):
        states = State(3)
        states.add('foo')
        self.assertEqual(states.from_name('foo'), states.FOO)


    def test_change(self):
        states = State(3)
        states.add('foo')
        states.add('bar')
        states.add('baz')
        states.alias('inky', states.FOO | states.BAR)
        states.alias('pinky', states.FOO | states.BAZ)
        states.put('abcd')
        states.next('abcd')
        states.set('abcd', states.BAR)
        states.change('abcd', states.BAZ, states.BAR)
        self.assertEqual(states.state('abcd'), states.PINKY)


    def test_change_onezero(self):
        states = State(3)
        states.add('foo')
        states.add('bar')
        states.add('baz')
        states.alias('inky', states.FOO | states.BAR)
        states.alias('pinky', states.FOO | states.BAZ)
        states.put('abcd')
        states.next('abcd')
        states.change('abcd', states.BAR, 0)
        self.assertEqual(states.state('abcd'), states.INKY)
        states.change('abcd', 0, states.BAR)
        self.assertEqual(states.state('abcd'), states.FOO)


    def test_change_dates(self):
        states = State(3)
        states.add('foo')
        states.put('abcd')
        states.put('bcde')

        a = states.modified('abcd')
        b = states.modified('bcde')
        self.assertGreater(b, a)

        states.set('abcd', states.FOO)
        a = states.modified('abcd')
        b = states.modified('bcde')
        self.assertGreater(a, b)


    def test_event_callback(self):
        cb = MockCallback()
        states = State(3, event_callback=cb.add)
        states.add('foo')
        states.add('bar')
        states.add('baz')
        states.alias('xyzzy', states.FOO | states.BAR)
        states.put('abcd')
        states.set('abcd', states.FOO)
        states.set('abcd', states.BAR)
        states.change('abcd', states.BAZ, states.XYZZY)
        events = cb.items['abcd']
        self.assertEqual(len(events), 4)
        self.assertEqual(events[0], states.NEW)
        self.assertEqual(events[1], states.FOO)
        self.assertEqual(events[2], states.XYZZY)
        self.assertEqual(events[3], states.BAZ)


    def test_dynamic(self):
        states = State(0)
        states.add('foo')
        states.add('bar')
        states.alias('baz', states.FOO | states.BAR)



    def test_mask(self):
        states = State(3)
        states.add('foo')
        states.add('bar')
        states.add('baz')
        states.alias('all', states.FOO | states.BAR | states.BAZ)
        mask = states.mask('xyzzy', states.FOO | states.BAZ)
        self.assertEqual(mask, states.BAR)


    def test_mask_dynamic(self):
        states = State(0)
        states.add('foo')
        states.add('bar')
        states.add('baz')
        states.alias('all', states.FOO | states.BAR | states.BAZ)
        mask = states.mask('xyzzy', states.FOO | states.BAZ)
        self.assertEqual(mask, states.BAR)


    def test_mask_zero(self):
        states = State(0)
        states.add('foo')
        states.add('bar')
        states.add('baz')
        states.alias('all', states.FOO | states.BAR | states.BAZ)
        mask = states.mask('xyzzy')
        self.assertEqual(mask, states.ALL)


if __name__ == '__main__':
    unittest.main()
