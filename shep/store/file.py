# standard imports
import os
import re

# local imports
from .base import (
        re_processedname,
        StoreFactory,
        )


class SimpleFileStore:
    """Filesystem store of contents for state, with one directory per state.

    :param path: Filesystem base path for all state directory
    :type path: str
    """
    def __init__(self, path, binary=False):
        self.__path = path
        os.makedirs(self.__path, exist_ok=True)
        if binary:
            self.__m = ['rb', 'wb']
        else:
            self.__m = ['r', 'w']


    def put(self, k, contents=None):
        """Add a new key and optional contents 

        :param k: Content key to add 
        :type k: str
        :param contents: Optional contents to assign for content key
        :type contents: any
        """
        fp = os.path.join(self.__path, k)
        if contents == None:
            if self.__m[1] == 'wb':
                contents = b''
            else:
                contents = ''

        f = open(fp, self.__m[1])
        f.write(contents)
        f.close()


    def remove(self, k):
        """Remove a content key from a state.

        :param k: Content key to remove from the state
        :type k: str
        :raises FileNotFoundError: Content key does not exist in the state
        """
        fp = os.path.join(self.__path, k)
        os.unlink(fp)

    
    def get(self, k):
        """Retrieve the content for the given content key.

        :param k: Content key to retrieve content for
        :type k: str
        :raises FileNotFoundError: Content key does not exist for the state
        :rtype: any
        :return: Contents
        """
        fp = os.path.join(self.__path, k)
        f = open(fp, self.__m[0])
        r = f.read()
        f.close()
        return r


    def list(self):
        """List all content keys persisted for the state.

        :rtype: list of str
        :return: Content keys in state
        """
        files = []
        for p in os.listdir(self.__path):
            fp = os.path.join(self.__path, p)
            f = open(fp, self.__m[0])
            r = f.read()
            f.close()
            if len(r) == 0:
                r = None
            files.append((p, r,))
        return files


    def path(self, k=None):
        """Return filesystem path for persisted state or state item.

        :param k: If given, will return filesystem path to specified content key
        :type k: str
        :rtype: str
        :return: File path
        """
        if k == None:
            return self.__path
        return os.path.join(self.__path, k)


    def replace(self, k, contents):
        """Replace persisted content for persisted content key.

        :param k: Content key to replace contents for
        :type k: str
        :param contents: Contents
        :type contents: any
        """
        fp = os.path.join(self.__path, k)
        os.stat(fp)
        f = open(fp, self.__m[1])
        r = f.write(contents)
        f.close()


    def modified(self, k):
        path = self.path(k)
        st = os.stat(path)
        return st.st_ctime


    def register_modify(self, k):
        pass


class SimpleFileStoreFactory(StoreFactory):
    """Provide a method to instantiate SimpleFileStore instances that provide persistence for individual states.

    :param path: Filesystem path as base path for states
    :type path: str
    """
    def __init__(self, path, binary=False):
        self.__path = path
        self.__binary = binary


    def add(self, k):
        """Create a new SimpleFileStore for a state.

        :param k: Identifier for the state
        :type k: str
        :rtype: SimpleFileStore
        :return: A filesystem persistence instance with the given identifier as subdirectory
        """
        k = str(k)
        store_path = os.path.join(self.__path, k)
        return SimpleFileStore(store_path, binary=self.__binary)


    def ls(self):
        r = []
        import sys
        for v in os.listdir(self.__path):
            if re.match(re_processedname, v):
                r.append(v)
        return r


    def close(self):
        pass
