# local imports
from .state import State
from .error import StateItemExists


class PersistedState(State):

    def __init__(self, factory, bits, logger=None):
        super(PersistedState, self).__init__(bits, logger=logger)
        self.__store_factory = factory
        self.__stores = {}


    def __ensure_store(self, k):
        if self.__stores.get(k) == None:
            self.__stores[k] = self.__store_factory(k)


    def put(self, key, contents=None, state=None, force=False):
        to_state = super(PersistedState, self).put(key, state=state, contents=contents, force=force)

        k = self.name(to_state)

        self.__ensure_store(k)
        self.__stores[k].add(key, contents, force=force)


    def set(self, key, or_state):
        from_state = self.state(key)
        k_from = self.name(from_state)

        to_state = super(PersistedState, self).set(key, or_state)
        k_to = self.name(to_state)
        self.__ensure_store(k_to)

        contents = self.__stores[k_from].get(key)
        self.__stores[k_to].add(key, contents)
        self.__stores[k_from].remove(key)

        return to_state


    def unset(self, key, not_state):
        from_state = self.state(key)
        k_from = self.name(from_state)

        to_state = super(PersistedState, self).unset(key, not_state)

        k_to = self.name(to_state)
        self.__ensure_store(k_to)

        contents = self.__stores[k_from].get(key)
        self.__stores[k_to].add(key, contents)
        self.__stores[k_from].remove(key)

        return to_state


    def move(self, key, to_state):
        from_state = self.state(key)
        to_state = super(PersistedState, self).move(key, to_state)
        return self.__movestore(key, from_state, to_state)


    def __movestore(self, key, from_state, to_state):
        k_from = self.name(from_state)
        k_to = self.name(to_state)

        self.__ensure_store(k_to)

        contents = self.__stores[k_from].get(key)
        self.__stores[k_to].add(key, contents)
        self.__stores[k_from].remove(key)

        return to_state


    def purge(self, key):
        state = self.state(key)
        k = self.name(state)

        self.__ensure_store(k)

        self.__stores[k].remove(key)
        super(PersistedState, self).purge(key)


    def sync(self, state):
        k = self.name(state)

        for o in self.__stores[k].list():
            try:
                super(PersistedState, self).put(o[0], state=state, contents=o[1])
            except StateItemExists:
                pass


    def path(self, state, key=None):
        k = self.name(state)

        return self.__stores[k].path(key=key)


    def next(self, key=None):
        from_state = self.state(key)
        to_state = super(PersistedState, self).next(key)
        return self.__movestore(key, from_state, to_state)
