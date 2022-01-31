class StateExists(Exception):
    pass


class StateInvalid(Exception):
    pass


class StateItemExists(Exception):
    pass


class StateItemNotFound(Exception):
    pass


class StateCorruptionError(RuntimeError):
    pass
