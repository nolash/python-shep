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


if __name__ == '__main__':
    unittest.main()
