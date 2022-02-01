# standard imports
import os


class SimpleFileStore:

    def __init__(self, path):
        self.path = path
        os.makedirs(self.path, exist_ok=True)


    def add(self, v, contents):
        if contents == None:
            contents = ''
        fp = os.path.join(self.path, v)
        try:
            os.stat(fp)
            raise FileExistsError(fp)
        except FileNotFoundError:
            pass
        f = open(fp, 'w')
        f.write(contents)
        f.close()


class SimpleFileStoreFactory:

    def __init__(self, path):
        self.path = path


    def add(self, k):
        k = str(k)
        store_path = os.path.join(self.path, k)
        return SimpleFileStore(store_path)
