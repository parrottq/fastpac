"""
Different mirror picker implementations
"""
from random import randrange


class SinglePicker:
    """
    Picks the fist mirror in the list everytime
    """
    def __init__(self, mirrors, arg=None):
        self._mirrors = mirrors

    def next(self, size=0):
        return self._mirrors[0]


class RandomPicker:
    """
    Picks a random mirror from the list
    """
    def __init__(self, mirrors, arg=None):
        self._mirrors = mirrors

    def next(self, size=0):
        return self._mirrors[randrange(0, len(self._mirrors))]

    def get_mirrors(self):
        return self._mirrors

    def remove(self, name):
        self._mirrors.remove(name)


class CounterPicker:
    """
    Picks mirror for a number of times before moving to the next one
    """
    def __init__(self, mirrors, arg=1):
        self.max = arg
        self.uses = 0
        self.current_item = 0
        self._mirrors = mirrors

    def next(self, size=0):

        if self.uses >= self.max:
            self.current_item += 1
            self.uses = 0
        self.uses += 1

        return self._mirrors[self.current_item % len(self._mirrors)]


class LeastUsedPicker:
    """
    The mirror that has been used the least taking package size into consideration
    """
    def __init__(self, mirrors, arg=None):
        self._mirrors = [[mirror, 0] for mirror in mirrors]

    def next(self, size=0):
        smallest = -1

        for num, (mirror, size_c) in enumerate(self._mirrors):
            if smallest == -1:
                smallest = 0
            elif size_c < self._mirrors[smallest][1]:
                smallest = num

        self._mirrors[smallest][1] += size
        return self._mirrors[smallest][0]


class CapPicker:
    """
    Gives each mirror a data cap in bytes
    """
    def __init__(self, mirrors, arg=0):
        self.cap = arg
        self._mirrors = [[mirror, 0] for mirror in mirrors]

    def next(self, size=0):
        if size > self.cap:
            return self._mirrors.pop(0)[0]

        for num, (mirror, quota) in enumerate(self._mirrors):
            if quota + size < self.cap:
                self._mirrors[num][1] += size
                return mirror

    def get_mirrors(self):
        return [mirror[0] for mirror in self._mirrors]
