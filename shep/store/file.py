# standard imports
import os


class SimpleFileStore:

    def __init__(self, path):
        self.__path = path
        os.makedirs(self.__path, exist_ok=True)


    def add(self, k, contents=None):
        fp = os.path.join(self.__path, k)
        if contents == None:
            contents = ''

        f = open(fp, 'w')
        f.write(contents)
        f.close()


    def remove(self, k):
        fp = os.path.join(self.__path, k)
        os.unlink(fp)


    def get(self, k):
        fp = os.path.join(self.__path, k)
        f = open(fp, 'r')
        r = f.read()
        f.close()
        return r


    def list(self):
        files = []
        for p in os.listdir(self.__path):
            fp = os.path.join(self.__path, p)
            f = open(fp, 'r')
            r = f.read()
            f.close()
            if len(r) == 0:
                r = None
            files.append((p, r,))
        return files


    def path(self, key=None):
        if key == None:
            return self.__path
        return os.path.join(self.__path, key)


    def replace(self, key, contents):
        fp = os.path.join(self.__path, key)
        os.stat(fp)
        f = open(fp, 'w')
        r = f.write(contents)
        f.close()


class SimpleFileStoreFactory:

    def __init__(self, path):
        self.__path = path


    def add(self, k):
        k = str(k)
        store_path = os.path.join(self.__path, k)
        return SimpleFileStore(store_path)
