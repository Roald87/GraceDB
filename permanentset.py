class PermanentSet(object):
    """
    Holds and saves a set of ints in a local text file.
    """

    def __init__(self, fname):
        self.fname = fname
        self.data = self.read()

    def read(self) -> set:
        data = set()
        try:
            with open(self.fname, 'r') as f:
                data = {int(num) for num in f.readlines()}
        except IOError:
            pass

        return data

    def is_in_list(self, number: int) -> bool:
        return number in self.data

    def add(self, number: int):
        self.data.add(number)
        self._save_data()

    def remove(self, number: int):
        self.data.remove(number)
        self._save_data()

    def _save_data(self):
        with open(self.fname, 'w') as f:
            f.write('\n'.join((str(num) for num in self.data)))
