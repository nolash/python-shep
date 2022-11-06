# standard imports
import unittest

# local imports
from shep import State
from shep.error import (
        StateTransitionInvalid,
        )


def mock_verify(state, key, from_state, to_state):
    if from_state == state.FOO:
        if to_state == state.BAR:
            return 'bar cannot follow foo'


class TestState(unittest.TestCase):

    def test_verify(self):
        states = State(2, verifier=mock_verify)
        states.add('foo')
        states.add('bar')
        states.put('xyzzy')
        states.next('xyzzy')
        with self.assertRaises(StateTransitionInvalid):
            states.next('xyzzy')



if __name__ == '__main__':
    unittest.main()
