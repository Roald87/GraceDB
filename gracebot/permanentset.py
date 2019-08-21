from typing import Union

PSet = Union[int, str]


class PermanentSet(object):
    """
    Holds and saves a set of ints in a local text file.
    """

    def __init__(self, fname: str, typ: type):
        self.fname = fname
        self.typ = typ
        self.data = self._read()

    def _read(self) -> set:
        data: set = set()
        try:
            with open(self.fname, "r") as f:
                data = {self.typ(num.rstrip()) for num in f.readlines()}
        except FileNotFoundError:
            with open(self.fname, "w") as _:
                pass

        return data

    def _save_data(self):
        with open(self.fname, "w") as f:
            f.write("\n".join((str(num) for num in self.data)))

    def add(self, number: PSet):
        self.data.add(number)
        self._save_data()

    def remove(self, number: PSet):
        try:
            self.data.remove(number)
            self._save_data()
        except KeyError:
            pass

    def is_in_list(self, number: PSet) -> bool:
        return number in self.data
