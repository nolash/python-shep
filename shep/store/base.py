re_processedname = r'^_?[A-Z\._]*$'


class StoreFactory:

    def __del__(self):
        self.close()


    def add(self, k):
        raise NotImplementedError()


    def close(self):
        pass


    def ls(self):
        raise NotImplementedError()
