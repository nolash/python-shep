# standard imports
import datetime

# local imports
from .state import State
from .error import (
        StateItemExists,
        StateLockedKey,
        )


class PersistedState(State):
    """Adapter for persisting state changes and synchronising states between memory and persisted backend.

    :param factory: A function capable of returning a persisted store from a single path argument.
    :type factory: function
    :param bits: Number of pure states. Passed to the superclass.
    :type bits: int
    :param logger: Logger to capture logging output, or None for no logging.
    :type logger: object
    """

    def __init__(self, factory, bits, logger=None, verifier=None, check_alias=True, event_callback=None):
        super(PersistedState, self).__init__(bits, logger=logger, verifier=verifier, check_alias=check_alias, event_callback=event_callback)
        self.__store_factory = factory
        self.__stores = {}


    # Create state store container if missing.
    def __ensure_store(self, k):
        if self.__stores.get(k) == None:
            self.__stores[k] = self.__store_factory(k)


    def put(self, key, contents=None, state=None):
        """Persist a key or key/content pair.

        See shep.state.State.put
        """
        k = self.to_name(state)

        self.__ensure_store(k)

        self.__stores[k].put(key, contents)

        super(PersistedState, self).put(key, state=state, contents=contents)

        self.register_modify(key)


    def set(self, key, or_state):
        """Persist a new state for a key or key/content.

        See shep.state.State.set
        """
        from_state = self.state(key)
        k_from = self.name(from_state)

        to_state = super(PersistedState, self).set(key, or_state)
        k_to = self.name(to_state)
        self.__ensure_store(k_to)

        contents = None
        try:
            contents = self.__stores[k_from].get(key)
            self.__stores[k_to].put(key, contents)
            self.__stores[k_from].remove(key)
        except StateLockedKey as e:
            super(PersistedState, self).unset(key, or_state, allow_base=True)
            raise e
       
        self.sync(to_state)

        return to_state


    def unset(self, key, not_state):
        """Persist a new state for a key or key/content.

        See shep.state.State.unset
        """
        from_state = self.state(key)
        k_from = self.name(from_state)

        to_state = super(PersistedState, self).unset(key, not_state)

        k_to = self.name(to_state)
        self.__ensure_store(k_to)

        contents = self.__stores[k_from].get(key)
        self.__stores[k_to].put(key, contents)
        self.__stores[k_from].remove(key)

        return to_state


    def change(self, key, bits_set, bits_unset):
        """Persist a new state for a key or key/content.

        See shep.state.State.unset
        """
        from_state = self.state(key)
        k_from = self.name(from_state)

        to_state = super(PersistedState, self).change(key, bits_set, bits_unset)

        k_to = self.name(to_state)
        self.__ensure_store(k_to)

        contents = self.__stores[k_from].get(key)
        self.__stores[k_to].put(key, contents)
        self.__stores[k_from].remove(key)

        self.register_modify(key)

        return to_state


    def move(self, key, to_state):
        """Persist a new state for a key or key/content.

        See shep.state.State.move
        """
        from_state = self.state(key)
        to_state = super(PersistedState, self).move(key, to_state)
        return self.__movestore(key, from_state, to_state)


    # common procedure for safely moving a persisted resource from one state to another.
    def __movestore(self, key, from_state, to_state):
        k_from = self.name(from_state)
        k_to = self.name(to_state)

        self.__ensure_store(k_to)

        contents = self.__stores[k_from].get(key)
        self.__stores[k_to].put(key, contents)
        self.__stores[k_from].remove(key)

        self.register_modify(key)

        self.sync(to_state)

        return to_state


    def sync(self, state=None, not_state=None):
        """Reload resources for a single state in memory from the persisted state store.

        :param state: State to load
        :type state: int
        :raises StateItemExists: A content key is already recorded with a different state in memory than in persisted store.
        # :todo: if sync state is none, sync all
        """

        states_numeric = []
        if state == None:
            states_numeric = list(self.all(numeric=True))
        else:
            states_numeric = [state]
       
        states = []
        for state in states_numeric:
            if not_state != None:
                if state & not_state == 0:
                    states.append(self.name(state))
            else:
                states.append(self.name(state))

        ks = []
        for k in states:
            ks.append(k)

        for k in ks:
            self.__ensure_store(k)
            for o in self.__stores[k].list():
                state = self.from_name(k)
                try:
                    super(PersistedState, self).put(o[0], state=state, contents=o[1])
                except StateItemExists as e:
                    pass


    def list(self, state):
        """List all content keys for a particular state.

        This method will return from memory, and will not sync the persisted state first.
   
        See shep.state.State.list
        """
        k = self.name(state)
        self.__ensure_store(k)
        return super(PersistedState, self).list(state)


    def path(self, state, key=None):
        """Return a file path or URL pointing to the persisted state.
        
        If the key is omitted, the URL to the state item's container must be returned, and None if no such container exists.
         
        :param state: State to locate
        :type state: int
        :param key: Content key to locate
        :type key: str
        :rtype: str
        :returns: Locator pointng to persisted state
        :todo: rename to "location"
        """
        k = self.name(state)
        self.__ensure_store(k)
        return self.__stores[k].path(k=key)


    def next(self, key=None):
        """Advance and persist to the next pure state.

        See shep.state.State.next
        """
        from_state = self.state(key)
        to_state = super(PersistedState, self).next(key)
        return self.__movestore(key, from_state, to_state)


    def replace(self, key, contents):
        """Replace contents associated by content key.

        See shep.state.State.replace
        """
        state = self.state(key)
        k = self.name(state)
        r = self.__stores[k].replace(key, contents)
        super(PersistedState, self).replace(key, contents)
        return r


    def modified(self, key):
        state = self.state(key)
        k = self.name(state)
        return self.__stores[k].modified(key)
