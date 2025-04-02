

def process_bar(finished:int|float, all:int|float, width:int|None = 20) -> None:
    """
    "finished" should be 
    """
    if finished < 0 or not isinstance(finished, (int, float)):
        raise ValueError("`finished` should be a positive number "
                         f"larger than or equal to 0. Got {finished}")
    elif all <= 0 or not isinstance(all, (int, float)):
        raise ValueError("`all` should be a positive number "
                         f"larger than 0. Got {all}")
    elif width <= 0 or not isinstance(width, int):
        raise ValueError("`width` should be a positive integer "
                         f"larger than 0. Got {width}")
    if width is None: return
    finished = finished / all * width
    finished_X = int(finished)
    finished_rest = finished - finished_X
    REST = "|/-\\|/-\\"
    print(
        f"[{"X" * finished_X}"
        f"{"" if finished_rest <= 1e-6
            else REST[int(finished_rest*len(REST))]}"
        f"{" " * int(width - finished)}]"
        "\033[F"
    )
if __name__ == "__main__":
    from time import sleep, time
    N = 500
    interval = 0.1
    start = time()
    for i in range(0, N + 1):
        sleep(interval)
        process_bar(i, N)
    overhead = time() - start
    start = time()
    for i in range(0, N + 1):
        sleep(interval)
    overhead = overhead - (time() - start)
    print(overhead)