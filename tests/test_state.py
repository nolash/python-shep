# standard imports
import unittest
import logging

# local imports
from shep import State
from shep.error import (
        StateExists,
        StateInvalid,
        StateItemNotFound,
        )

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()


class MockCallback:

    def __init__(self):
        self.items = {}
        self.items_from = {}


    def add(self, k, v_from, v_to):
        if self.items.get(k) == None:
            self.items[k] = []
            self.items_from[k] = []
        self.items[k].append(v_to)
        self.items_from[k].append(v_from)


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
        states.add('baz')
        states.put('abcd')
        states.set('abcd', states.FOO)
        states.set('abcd', states.BAZ)
        v = states.state('abcd')
        s = states.name(v)
        self.assertEqual(s, '_FOO__BAZ')


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
        self.assertEqual(states.from_name(events[0]), states.NEW)
        self.assertEqual(states.from_name(events[1]), states.FOO)
        self.assertEqual(states.from_name(events[2]), states.XYZZY)
        self.assertEqual(states.from_name(events[3]), states.BAZ)


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


    def test_remove(self):
        states = State(1)
        states.add('foo')

        states.put('xyzzy', contents='plugh')
        v = states.get('xyzzy')
        self.assertEqual(v, 'plugh')

        states.next('xyzzy')

        v = states.state('xyzzy')
        self.assertEqual(states.FOO, v)

        states.purge('xyzzy')
       
        with self.assertRaises(StateItemNotFound):
            states.state('xyzzy')


    def test_elements(self):
        states = State(2)
        states.add('foo')
        states.add('bar')
        states.alias('baz', states.FOO, states.BAR)

        v = states.elements(states.BAZ)
        self.assertIn('FOO', v)
        self.assertIn('BAR', v)
        self.assertIsInstance(v, str)

        v = states.elements(states.BAZ, numeric=True)
        self.assertIn(states.FOO, v)
        self.assertIn(states.BAR, v)

        v = states.elements(states.BAZ, as_string=False)
        self.assertIn('FOO', v)
        self.assertIn('BAR', v)
        self.assertNotIsInstance(v, str)
        self.assertIsInstance(v, list)


    def test_count(self):
        states = State(3)
        states.add('foo')
        states.add('bar')
        self.assertEqual(states.count(), 2)
        states.add('baz')
        self.assertEqual(states.count(), 3)


    def test_pure(self):
        states = State(2)
        states.add('foo')
        states.add('bar')
        states.alias('baz', states.FOO, states.BAR)

        v = states.is_pure(states.BAZ)
        self.assertFalse(v)

        v = states.is_pure(states.FOO)
        self.assertTrue(v)


    def test_default(self):
        states = State(2, default_state='FOO')
        with self.assertRaises(StateItemNotFound):
            states.state('NEW')
        r = getattr(states, 'FOO')
        self.assertEqual(r, 0)
        states.state('FOO')
        states.put('bar')
        r = states.list(states.FOO)
        self.assertEqual(len(r), 1)


    def test_unset(self):
        states = State(2)
        states.add('one')
        states.add('two')
        states.alias('three', states.ONE, states.TWO)
        states.put('foo', state=states.ONE)
        states.set('foo', states.TWO)
        r = states.list(states.ONE)
        self.assertEqual(len(r), 1)
        r = states.list(states.TWO)
        self.assertEqual(len(r), 1)
        r = states.unset('foo', states.ONE)
        r = states.list(states.ONE)
        self.assertEqual(len(r), 0)
        r = states.list(states.TWO)
        self.assertEqual(len(r), 1)


    def test_move(self):
        states = State(1)
        states.add('one')
        states.put('foo')
        r = states.list(states.NEW)
        self.assertEqual(len(r), 1)
        states.move('foo', states.ONE)
        r = states.list(states.NEW)
        self.assertEqual(len(r), 0)



    def test_generate_missing(self):
        states = State(3)
        with self.assertRaises(StateInvalid):
            states.from_elements("_FOO__BAR")
        states.from_elements("_FOO__BAR", create_missing=True)


    def test_set_same(self):
        states = State(4, check_alias=False)
        states.add('one')
        states.add('two')
        states.add('three')
        states.put('foo')
        states.next('foo')
        self.assertEqual(states.state('foo'), states.ONE)
        states.set('foo', states.TWO)
        self.assertEqual(states.state('foo'), states.ONE | states.TWO)
        self.assertEqual(states.state('foo'), states._ONE__TWO)

        states.alias('onetwo', states.ONE, states.TWO)
        states.set('foo', states.TWO)
        self.assertEqual(states.state('foo'), states.ONETWO)
        self.assertEqual(states.state('foo'), states._ONE__TWO)


if __name__ == '__main__':
    unittest.main()
