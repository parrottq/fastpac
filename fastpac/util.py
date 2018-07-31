"""
Utility functions
"""

class HybridGenerator:
    """
    Self expanding list
    """
    def __init__(self, generator):
        self._gen = generator
        self.cache = []

    def __iter__(self):
        def generator():
            # Use items already generated
            for item in self.cache:
                yield item

            # Generate new items
            for item in self._gen:
                self.cache.append(item)
                yield item

        return generator()

    def __getitem__(self, index):
        if index < len(self.cache):
            return self.cache[index]

        for item in self._gen:
            self.cache.append(item)
            if index < len(self.cache):
                return self.cache[index]
