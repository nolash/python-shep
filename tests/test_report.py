# standard imports
import unittest

# local imports
from shep import State
from shep.error import (
        StateExists,
        StateInvalid,
        )


class TestStateReport(unittest.TestCase):
        
    def setUp(self):
        self.states = State(4)
        self.states.add('foo') 
        self.states.add('bar') 
        self.states.add('baz') 


    def test_list_pure(self):
        for k in ['FOO', 'BAR', 'BAZ']:
            getattr(self.states, k)


    def test_list_alias(self):
        self.states.alias('xyzzy', self.states.FOO | self.states.BAZ)
        for k in ['FOO', 'BAR', 'BAZ', 'XYZZY']:
            getattr(self.states, k)


    def test_match(self):
        r = self.states.match(self.states.FOO)
        self.assertEqual(getattr(self.states, r[0]), 1)


    def test_match_alias(self):
        self.states.alias('xyzzy', self.states.FOO | self.states.BAZ)
        r = self.states.match(self.states.XYZZY)
        for k in ['FOO', 'BAZ']:
            self.assertIn(k, r[1])
        self.assertNotIn('BAR', r[1])
        self.assertEqual('XYZZY', r[0])


    def test_match_alias_pure(self):
        self.states.alias('xyzzy', self.states.FOO | self.states.BAZ)
        r = self.states.match(self.states.XYZZY, pure=True)
        for k in ['FOO', 'BAZ']:
            self.assertIn(k, r[1])
        self.assertNotIn('XYZZY', r[1])
        self.assertIsNone(r[0])


if __name__ == '__main__':
    unittest.main()
