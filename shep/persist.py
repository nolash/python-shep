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


    def put(self, item, state=None):
        k = self.name(state)
        self.__ensure_store(k)
        self.__stores[k].add(item)

        super(PersistedState, self).put(item, state=state)


    def move(self, item, to_state):
        k_to = self.name(to_state)

        from_state = self.state(item)
        k_from = self.name(from_state)

        self.__ensure_store(k_to)
        self.__ensure_store(k_from)

        self.__stores[k_to].add(item)
        self.__stores[k_from].remove(item)

        super(PersistedState, self).move(item, to_state)


    def purge(self, item):
        state = self.state(item)
        k = self.name(state)

        self.__ensure_store(k)

        self.__stores[k].remove(item)
        super(PersistedState, self).purge(item)
