import pytest
from fastpac.util import HybridGenerator


def test_hybrid_as_new_generator():
    def generator():
        for e in [0, 1, 2]:
            yield e

    gen = HybridGenerator(generator())
    new_gen_1 = iter(gen)
    new_gen_2 = iter(gen)

    assert next(new_gen_1) == 0
    assert next(new_gen_1) == 1
    assert next(new_gen_1) == 2

    assert next(new_gen_2) == 0
    assert next(new_gen_2) == 1
    assert next(new_gen_2) == 2

def test_hybrid_as_list():
    def generator():
        for e in [0, 1, 2]:
            yield e

    gen = HybridGenerator(generator())

    assert gen[0] == 0
    assert gen.cache == [0]
    assert gen[2] == 2
    assert gen.cache == [0, 1, 2]
    assert gen[1] == 1
    assert gen.cache == [0, 1, 2]

def test_hybrid_cache():
    def generator():
        for e in [0, 1, 2]:
            yield e

    gen = HybridGenerator(generator())
    new_gen = iter(gen)

    assert gen.cache == []

    next(new_gen)
    assert gen.cache == [0]

    next(new_gen)
    assert gen.cache == [0, 1]

    next(new_gen)
    assert gen.cache == [0, 1, 2]

