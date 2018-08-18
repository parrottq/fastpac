"""
Utility functions
"""

from concurrent.futures import ThreadPoolExecutor
import sys
import traceback

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


class ThreadPoolExecutorStackTraced(ThreadPoolExecutor):

    def submit(self, fn, *args, **kwargs):
        """Submits the wrapped function instead of `fn`"""

        return super(ThreadPoolExecutorStackTraced, self).submit(
            self._function_wrapper, fn, *args, **kwargs)

    def _function_wrapper(self, fn, *args, **kwargs):
        """Wraps `fn` in order to preserve the traceback of any kind of
        raised exception

        """
        try:
            return fn(*args, **kwargs)
        except Exception:
            raise sys.exc_info()[0](traceback.format_exc())  # Creates an
                                                             # exception of the
                                                             # same type with the
                                                             # traceback as
                                                             # message
