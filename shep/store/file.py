# standard imports
import os


class SimpleFileStore:

    def __init__(self, path):
        self.__path = path
        os.makedirs(self.__path, exist_ok=True)


    def add(self, k, contents=None, force=False):
        fp = os.path.join(self.__path, k)
        have_file = False
        try:
            os.stat(fp)
            have_file = True
        except FileNotFoundError:
            pass

        if have_file:
            if not force:
                raise FileExistsError(fp)
            if contents == None:
                raise FileExistsError('will not overwrite empty content on existing file {}. Use rm then add instead'.format(fp))
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


class SimpleFileStoreFactory:

    def __init__(self, path):
        self.__path = path


    def add(self, k):
        k = str(k)
        store_path = os.path.join(self.__path, k)
        return SimpleFileStore(store_path)
