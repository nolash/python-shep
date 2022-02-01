# local imports
from .state import State


class PersistedState(State):

    def __init__(self, factory, bits, logger=None):
        super(PersistedState, self).__init__(bits, logger=logger)
        self.__store_factory = factory
        self.__stores = {}


    def __ensure_store(self, k):
        if self.__stores.get(k) == None:
            self.__stores[k] = self.__store_factory(k)


    def put(self, key, contents=None, state=None, force=False):
        k = self.name(state)
        self.__ensure_store(k)
        self.__stores[k].add(key, contents, force=force)

        super(PersistedState, self).put(key, state=state, contents=contents, force=force)


    def move(self, key, to_state):
        k_to = self.name(to_state)

        from_state = self.state(key)
        k_from = self.name(from_state)

        self.__ensure_store(k_to)
        self.__ensure_store(k_from)

        contents = self.__stores[k_from].get(key)
        self.__stores[k_to].add(key, contents)
        self.__stores[k_from].remove(key)

        super(PersistedState, self).move(key, to_state)


    def purge(self, key):
        state = self.state(key)
        k = self.name(state)

        self.__ensure_store(k)

        self.__stores[k].remove(key)
        super(PersistedState, self).purge(key)
