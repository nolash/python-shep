# standard imports
import os
import re

# local imports
from .base import (
        re_processedname,
        StoreFactory,
        )
from shep.error import StateLockedKey


class SimpleFileStore:
    """Filesystem store of contents for state, with one directory per state.

    :param path: Filesystem base path for all state directory
    :type path: str
    """
    def __init__(self, path, binary=False, lock_path=None):
        self.__path = path
        os.makedirs(self.__path, exist_ok=True)
        if binary:
            self.__m = ['rb', 'wb']
        else:
            self.__m = ['r', 'w']
        self.__lock_path = lock_path
        if self.__lock_path != None:
            os.makedirs(lock_path, exist_ok=True)


    def __is_locked(self, k):
        if self.__lock_path == None:
            return False
        for v in os.listdir(self.__lock_path):
            if k == v:
                return True
        return False
       

    def __lock(self, k):
        if self.__lock_path == None:
            return
        if self.__is_locked(k):
            raise StateLockedKey(k)
        fp = os.path.join(self.__lock_path, k)
        f = open(fp, 'w')
        f.close()


    def __unlock(self, k):
        if self.__lock_path == None:
            return
        fp = os.path.join(self.__lock_path, k)
        try:
            os.unlink(fp)
        except FileNotFoundError:
            pass
        

    def put(self, k, contents=None):
        """Add a new key and optional contents 

        :param k: Content key to add 
        :type k: str
        :param contents: Optional contents to assign for content key
        :type contents: any
        """
        self.__lock(k)
        fp = os.path.join(self.__path, k)
        if contents == None:
            if self.__m[1] == 'wb':
                contents = b''
            else:
                contents = ''

        f = open(fp, self.__m[1])
        f.write(contents)
        f.close()
        self.__unlock(k)


    def remove(self, k):
        """Remove a content key from a state.

        :param k: Content key to remove from the state
        :type k: str
        :raises FileNotFoundError: Content key does not exist in the state
        """
        self.__lock(k)
        fp = os.path.join(self.__path, k)
        os.unlink(fp)
        self.__unlock(k)

    
    def get(self, k):
        """Retrieve the content for the given content key.

        :param k: Content key to retrieve content for
        :type k: str
        :raises FileNotFoundError: Content key does not exist for the state
        :rtype: any
        :return: Contents
        """
        self.__lock(k)
        fp = os.path.join(self.__path, k)
        f = open(fp, self.__m[0])
        r = f.read()
        f.close()
        self.__unlock(k)
        return r


    def list(self):
        """List all content keys persisted for the state.

        :rtype: list of str
        :return: Content keys in state
        """
        self.__lock('.list')
        files = []
        for p in os.listdir(self.__path):
            fp = os.path.join(self.__path, p)
            f = open(fp, self.__m[0])
            r = f.read()
            f.close()
            if len(r) == 0:
                r = None
            files.append((p, r,))
        self.__unlock('.list')
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
        self.__lock(k)
        fp = os.path.join(self.__path, k)
        os.stat(fp)
        f = open(fp, self.__m[1])
        r = f.write(contents)
        f.close()
        self.__unlock(k)


    def modified(self, k):
        self.__lock(k)
        path = self.path(k)
        st = os.stat(path)
        self.__unlock(k)
        return st.st_ctime


    def register_modify(self, k):
        pass


class SimpleFileStoreFactory(StoreFactory):
    """Provide a method to instantiate SimpleFileStore instances that provide persistence for individual states.

    :param path: Filesystem path as base path for states
    :type path: str
    """
    def __init__(self, path, binary=False, use_lock=False):
        self.__path = path
        self.__binary = binary
        self.__use_lock = use_lock


    def add(self, k):
        """Create a new SimpleFileStore for a state.

        :param k: Identifier for the state
        :type k: str
        :rtype: SimpleFileStore
        :return: A filesystem persistence instance with the given identifier as subdirectory
        """
        lock_path = None
        if self.__use_lock:
            lock_path = os.path.join(self.__path, '.lock')

        k = str(k)
        store_path = os.path.join(self.__path, k)
        return SimpleFileStore(store_path, binary=self.__binary, lock_path=lock_path)


    def ls(self):
        r = []
        for v in os.listdir(self.__path):
            if re.match(re_processedname, v):
                r.append(v)
        return r


    def close(self):
        pass
