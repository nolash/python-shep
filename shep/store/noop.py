# local imports
from .base import StoreFactory


class NoopStore:

    def put(self, k, contents=None):
        pass


    def remove(self, k):
        pass

    def get(self, k):
        pass


    def list(self):
        return []


    def path(self):
        return None


    def replace(self, k, contents):
        pass

    def modified(self, k):
        pass


    def register_modify(self, k):
        pass


class NoopStoreFactory(StoreFactory):

    def add(self, k):
        return NoopStore()


    def ls(self):
        return []
