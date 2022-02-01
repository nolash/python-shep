# standard imports
import os


class SimpleFileStore:

    def __init__(self, path):
        self.path = path
        os.makedirs(self.path, exist_ok=True)


    def add(self, k, contents=None, force=False):
        fp = os.path.join(self.path, k)
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
        elif contents == None:
            contents = ''

        f = open(fp, 'w')
        f.write(contents)
        f.close()


    def remove(self, k):
        fp = os.path.join(self.path, k)
        os.unlink(fp)


    def get(self, k):
        fp = os.path.join(self.path, k)
        f = open(fp, 'r')
        r = f.read()
        f.close()
        return r


    def list(self):
        files = []
        for p in os.listdir(self.path):
            fp = os.path.join(self.path, p)
            f = open(fp, 'r')
            r = f.read()
            f.close()
            if len(r) == 0:
                r = None
            files.append((p, r,))
        return files


class SimpleFileStoreFactory:

    def __init__(self, path):
        self.path = path


    def add(self, k):
        k = str(k)
        store_path = os.path.join(self.path, k)
        return SimpleFileStore(store_path)
