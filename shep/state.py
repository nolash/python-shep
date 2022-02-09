# local imports
from shep.error import (
        StateExists,
        StateInvalid,
        StateItemExists,
        StateItemNotFound,
        )


class State:
    """State is an in-memory bitmasked state store for key-value pairs, or even just keys alone.

    A State is comprised of a number of atomic state bits, and zero or more aliases that represent unique combinations of these bits.

    The State object will enforce that duplicate states cannot exist. It will also enforce that all alias states are composed of valid atomic states.

    :param bits: Number of atomic states that this State object will represent (i.e. number of bits).
    :type bits: int
    :param logger: Standard library logging instance to output to
    :type logger: logging.Logger
    """
    def __init__(self, bits, logger=None):
        self.__bits = bits
        self.__limit = (1 << bits) - 1
        self.__c = 0
        self.NEW = 0

        self.__reverse = {0: self.NEW}
        self.__keys = {self.NEW: []}
        self.__keys_reverse = {}
        self.__contents = {}


    # return true if v is a single-bit state
    def __is_pure(self, v):
        if v == 0:
            return True
        c = 1
        for i in range(self.__bits):
            if c & v > 0:
                break
            c <<= 1
        return c == v


    # validates a state name and return its canonical representation
    def __check_name_valid(self, k):
        if not k.isalpha():
            raise ValueError('only alpha')
        return k.upper()


    # enforces name validity, aswell as name uniqueness
    def __check_name(self, k):
        k = self.__check_name_valid(k) 
            
        try:
            getattr(self, k)
            raise StateExists(k)
        except AttributeError:
            pass
        return k


    # enforces state value validity and uniqueness
    def __check_valid(self, v):
        v = self.__check_value_typ(v)
        if self.__reverse.get(v):
            raise StateExists(v)
        return v


    # enforces state value within bit limit of instantiation
    def __check_limit(self, v):
        if v > self.__limit:
            raise OverflowError(v)
        return v


    # enforces state value validity, uniqueness and value limit 
    def __check_value(self, v):
        v = self.__check_valid(v)
        self.__check_limit(v) 
        return v


    # enforces state value validity
    def __check_value_typ(self, v):
        return int(v)


    # enforces state value validity within the currently registered states (number of add calls vs number of bits in instantiation).
    def __check_value_cursor(self, v):
        v = self.__check_value_typ(v)
        if v > 1 << self.__c:
            raise StateInvalid(v)
        return v


    # set a bit for state of the given key
    def __set(self, k, v):
        setattr(self, k, v)
        self.__reverse[v] = k
        self.__c += 1


    # check validity of key to register state for
    def __check_key(self, item):
        if self.__keys_reverse.get(item) != None:
            raise StateItemExists(item)


    # adds a new key to the state store
    def __add_state_list(self, state, item):
        if self.__keys.get(state) == None:
            self.__keys[state] = []
        self.__keys[state].append(item)
        self.__keys_reverse[item] = state


    # Get index of a key for a given state.
    # A key should only ever exist in one state.
    # A failed lookup should indicate a mistake on the caller part, (it may also indicate corruption, but probanbly impossible to tell the difference)
    def __state_list_index(self, item, state_list):
        idx = -1
        try:
            idx = state_list.index(item)
        except ValueError:
            pass

        if idx == -1:
            raise StateCorruptionError() # should have state int here as value

        return idx


    # Add a state to the store.
    #
    # :param k: State name
    # :type k: str
    # :raises shep.error.StateExists: State name is already registered
    def add(self, k):
        v = 1 << self.__c
        k = self.__check_name(k)
        v = self.__check_value(v)
        self.__set(k, v)
        

    # Add an alias for a combination of states in the store.
    #
    # State aggregates may be provided as comma separated values or as a single (or'd) integer value. 
    #|
    # :param k: Alias name
    # :type k: str
    # :param *args: One or more states to aggregate for this alias.
    # :type *args: int or list of ints
    # :raises StateInvalid: Attempt to create alias for one or more atomic states that do not exist.
    # :raises ValueError: Attempt to use bit value as alias
    def alias(self, k, *args):
        k = self.__check_name(k)
        v = 0
        for a in args:
            a = self.__check_value_cursor(a)
            v = self.__check_limit(v | a)
        if self.__is_pure(v):
            raise ValueError('use add to add pure values')
        self.__set(k, v)


    # Return list of all unique atomic and alias states.
    #
    # :rtype: list of ints
    # :return: states
    def all(self):
        l = []
        for k in dir(self):
            if k[0] == '_':
                continue
            if k.upper() != k:
                continue
            l.append(k)
        l.sort()
        return l


    # Retrieve that string representation of the state attribute represented by the given state integer value.
    # 
    # :param v: State integer
    # :type v: int
    # :raises StateInvalid: State corresponding to given integer not found
    # :rtype: str
    # :return: State name
    def name(self, v):
        if v == None or v == 0:
            return 'NEW'
        k = self.__reverse.get(v)
        if k == None:
            raise StateInvalid(v)
        return k


    # Retrieve the real state integer value corresponding to an attribute name.
    #
    # :param k: Attribute name
    # :type k: str
    # :raises ValueError: Invalid attribute name
    # :raises AttributeError: Attribute not found
    # :rtype: int
    # :return: Numeric state value
    def from_name(self, k):
        k = self.__check_name_valid(k)
        return getattr(self, k)


    # Match against all stored states.
    #
    # If pure is set, only match against the single atomic state will be returned.
    #
    # :param v: Integer state to match
    # :type v: int
    # :param pure: Match only pure states
    # :type pure: bool
    # :raises KeyError: Unknown state
    # :rtype: tuple
    # :return: 0: Alias that input resolves to, 1: list of atomic states that matches the state
    def match(self, v, pure=False):
        alias = None
        if not pure:
            alias = self.__reverse.get(v)

        r = []
        c = 1
        for i in range(self.__bits):
            if v & c > 0:
                try:
                    k = self.__reverse[c]
                    r.append(k)
                except KeyError:
                    pass
            c <<= 1

        return (alias, r,)

   
    # Add a key to an existing state.
    #
    # If no state it specified, the default state attribute "NEW" will be used.
    # 
    # Contents may be supplied as value to pair with the given key. Contents may be changed later by calling the `replace` method.
    #
    # :param key: Content key to add
    # :type key: str
    # :param state: Initial state for the put. If not given, initial state will be NEW
    # :type state: int
    # :param contents: Contents to associate with key. A valie of None should be recognized as an undefined value as opposed to a zero-length value throughout any backend
    # :type contents: str
    # :raises StateItemExists: Content key has already been added
    # :raises StateInvalid: Given state has not been registered
    # :rtype: integer
    # :return: Resulting state that key is put under (should match the input state)
    def put(self, key, state=None, contents=None):
        if state == None:
            state = self.NEW
        elif self.__reverse.get(state) == None:
            raise StateInvalid(state)
        self.__check_key(key)
        self.__add_state_list(state, key)
        if contents != None:
            self.__contents[key] = contents

        return state
                                

    # Move a given content key from one state to another.
    #
    # :param key: Key to move
    # :type key: str
    # :param to_state: Numeric state to move to (may be atomic or alias)
    # :type to_state: integer
    # :raises StateItemNotFound: Given key has not been registered
    # :raises StateInvalid: Given state has not been registered
    # :rtype: integer
    # :return: Resulting state from move (should match the state given as input)
    def move(self, key, to_state):
        current_state = self.__keys_reverse.get(key)
        if current_state == None:
            raise StateItemNotFound(key)

        new_state = self.__reverse.get(to_state)
        if new_state == None:
            raise StateInvalid(to_state)

        return self.__move(key, current_state, to_state)


    # implementation for state move that ensures integrity of keys and states.
    def __move(self, key, from_state, to_state):
        current_state_list = self.__keys.get(from_state)
        if current_state_list == None:
            raise StateCorruptionError(current_state)

        idx = self.__state_list_index(key, current_state_list)

        new_state_list = self.__keys.get(to_state)
        if current_state_list == None:
            raise StateCorruptionError(to_state)

        self.__add_state_list(to_state, key)
        current_state_list.pop(idx) 

        return to_state
   

    # Move to an alias state by setting a single bit.
    #
    # :param key: Content key to modify state for
    # :type key: str
    # :param or_state: Atomic stat to add
    # :type or_state: int
    # :raises ValueError: State is not a single bit state
    # :raises StateItemNotFound: Content key is not registered
    # :raises StateInvalid: Resulting state after addition of atomic state is unknown
    # :rtype: int
    # :returns: Resulting state
    def set(self, key, or_state):
        if not self.__is_pure(or_state):
            raise ValueError('can only apply using single bit states')

        current_state = self.__keys_reverse.get(key)
        if current_state == None:
            raise StateItemNotFound(key)

        to_state = current_state | or_state
        new_state = self.__reverse.get(to_state)
        if new_state == None:
            raise StateInvalid('resulting to state is unknown: {}'.format(to_state))

        return self.__move(key, current_state, to_state)

    
    # Unset a single bit, moving to a pure or alias state.
    #
    # The resulting state cannot be NEW (0).
    # 
    # :param key: Content key to modify state for
    # :type key: str
    # :param or_state: Atomic stat to add
    # :type or_state: int
    # :raises ValueError: State is not a single bit state, or attempts to revert to NEW
    # :raises StateItemNotFound: Content key is not registered
    # :raises StateInvalid: Resulting state after addition of atomic state is unknown
    # :rtype: int
    # :returns: Resulting state
    def unset(self, key, not_state):
        if not self.__is_pure(not_state):
            raise ValueError('can only apply using single bit states')

        current_state = self.__keys_reverse.get(key)
        if current_state == None:
            raise StateItemNotFound(key)

        to_state = current_state & (~not_state)
        if to_state == current_state:
            raise ValueError('invalid change for state {}: {}'.format(key, not_state))

        if to_state == self.NEW:
            raise ValueError('State {} for {} cannot be reverted to NEW'.format(current_state, key))

        new_state = self.__reverse.get(to_state)
        if new_state == None:
            raise StateInvalid('resulting to state is unknown: {}'.format(to_state))

        return self.__move(key, current_state, to_state)


    # Return the current numeric state for the given content key.
    #
    # :param key: Key to return content for
    # :type key: str
    # :raises StateItemNotFound: Content key is unknown
    # :rtype: int
    # :returns: State
    def state(self, key):
        state = self.__keys_reverse.get(key)
        if state == None:
            raise StateItemNotFound(key)
        return state


    # Retrieve the content for a content key.
    # 
    # :param key: Content key to retrieve content for
    # :type key: str
    # :rtype: any
    # :returns: Content
    def get(self, key):
        return self.__contents.get(key)


    # List all content keys matching a state.
    #
    # :param state: State to match 
    # :type state: int
    # :rtype: list of str
    # :returns: Matching content keys
    def list(self, state):
        try:
            return self.__keys[state]
        except KeyError:
            return []


    # Noop method for interface implementation providing sync to backend.
    #
    # :param state: State to sync.
    # :type state:
    # :todo: (for higher level implementer) if sync state is none, sync all
    def sync(self, state):
        pass


    # In the memory-only class no persisted state is used, and this will return None.
    # 
    # See shep.persist.PersistedState.path for more information.
    def path(self, state, key=None):
        return None


    # Return the next pure state.
    # 
    # Will return the same result as the method next, but without advancing to the new state.
    #
    # :param key: Content key to inspect state for
    # :type key: str
    # :raises StateItemNotFound: Unknown content key
    # :raises StateInvalid: Attempt to advance from an alias state, OR beyond the last known pure state.
    # :rtype: int
    # :returns: Next state
    def peek(self, key):
        state = self.__keys_reverse.get(key)
        if state == None:
            raise StateItemNotFound(key)
        if not self.__is_pure(state):
            raise StateInvalid('cannot run next on an alias state')
       
        if state == 0:
            state = 1
        else:
            state <<= 1
        if state > self.__c:
            raise StateInvalid('unknown state {}'.format(state))

        return state


    # Advance to the next pure state.
    #
    # :param key: Content key to inspect state for
    # :type key: str
    # :raises StateItemNotFound: Unknown content key
    # :raises StateInvalid: Attempt to advance from an alias state, OR beyond the last known pure state.
    # :rtype: int
    # :returns: Next state
    def next(self, key):
        from_state = self.state(key)
        new_state = self.peek(key)
        return self.__move(key, from_state, new_state)


    # Replace contents associated by content key.
    # 
    # :param key: Content key to replace for
    # :type key: str
    # :param contents: New contents
    # :type contents: any
    # :raises KeyError: Unknown content key
    def replace(self, key, contents):
        self.state(key)
        self.__contents[key] = contents
