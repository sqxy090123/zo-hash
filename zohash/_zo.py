import random
from ._hash import memory_hash_256, file_hash_256

I = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-"

class ZO(str):
    pass

def int2zo1(a: int) -> ZO:
    if a < 0:
        return '-' + int2zo1(-a) # type: ignore
    if a == 0:
        return ZO('0')
    digits = []
    while a > 0:
        digits.append(I[a % 64])
        a //= 64
    return ZO(''.join(reversed(digits)))

def rf(pth):
    with open(pth, "rb") as o:
        x = o.read()
        return x, len(x), sum(x)

def zo3sum(pth: str) -> ZO:
    h = file_hash_256(pth)
    return int2zo1(h)

def zo4sum(pth: str) -> str:
    data, length, total = rf(pth)
    if length == 0:
        return int2zo1(0) + "|" + int2zo1(0)

    fnv_hash = memory_hash_256(data)
    part1 = int2zo1(fnv_hash)

    seed = hash((length, total, fnv_hash)) & 0xFFFFFFFF
    rng = random.Random(seed)

    k = rng.randint(1, 128)
    sampled_sum = 0
    for _ in range(k):
        idx = rng.randint(0, length - 1)
        sampled_sum += data[idx]

    part2 = int2zo1(sampled_sum)
    return f"{part1}|{part2}"

if __name__ == "__main__":
    import sys
    file_path = sys.argv[1]
    result = zo4sum(file_path)
    print(f"zo4 value for file {file_path}: {result}")