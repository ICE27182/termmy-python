

from timeit import timeit
from collections import namedtuple
from random import sample, seed

Result = namedtuple("Result", ("colored_string", "random_read", "random_write"))
def benchmark(cls, n: int, *args,  **kwargs) -> tuple[float]:
    print(f"Start to construct{cls}")
    obj = cls(*args, **kwargs)
    print(f"Construction Done")
    print(f"Start to initiating frame")
    data = obj.data
    size = len(obj)
    for i in range(size):
        data[i] = (i % 7 ^ i) % 255
    print(f"Frame initiation done")

    seed(0)
    order = sample(range(0, channel_num*size, channel_num), size)
    forloop_overhead = timeit("for i in order: pass",
                              number=1000*n, 
                              globals=locals())
    print(len(order) * n * 1000)
    seed(1)
    order = sample(range(0, channel_num*size, channel_num), size)
    time_random_read = timeit(
                              "for i in order: data[i]; data[i+1]; data[i+2]",
                              number=1000*n, 
                              globals=locals(),)
    seed(2)
    order = sample(range(0, channel_num*size, channel_num), size)
    time_random_write = timeit(
                               "for i in order: data[i] = i&1; data[i+1] = i&2; data[i+2] = i&3",
                               number=1000*n,
                               globals=locals()) - forloop_overhead
    time_colored_string = timeit("obj.colored_string()", number=n, globals=locals())
    return Result(time_colored_string, time_random_read, time_random_write)


