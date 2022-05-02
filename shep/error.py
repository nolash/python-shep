class StateExists(Exception):
    """Attempt to add state that already exists.
    """
    pass


class StateInvalid(Exception):
    """Attempt to operate on or move to a state that does not exist.
    """
    pass


class StateItemExists(Exception):
    """A content key attempted added that already exists.
    """
    pass


class StateItemNotFound(Exception):
    """A content key attempted read that does not exist.
    """
    pass


class StateCorruptionError(RuntimeError):
    """An irrecoverable discrepancy between persisted state and memory state has occurred.
    """
    pass


class StateTransitionInvalid(Exception):
    """Raised if state transition verification fails
    """
    pass


class StateLockedKey(Exception):
    """Attempt to write to a state key that is being written to by another client
    """
    pass
