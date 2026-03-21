"""
ZO编码及基于海绵哈希的增强哈希功能
提供将整数转换为自定义base64字符串的函数，以及两种文件哈希方法：
- zo_basev1: 直接使用filehash_256v1哈希的base64表示
- zo1: 在哈希基础上增加随机采样校验
"""

import random
from ._hash import memoryhash_256v2, filehash_256v1

# 自定义base64字符集（URL安全，不含+/）
_BASE64_CHARSET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-"

class ZO(str):
    """ZO编码字符串类型，用于类型区分"""
    pass

def int_to_zo(value: int) -> ZO:
    """
    将整数转换为ZO编码（base64风格，字符集见_BASE64_CHARSET）
    :param value: 非负整数
    :return: ZO编码字符串
    """
    if value < 0:
        return '-' + int_to_zo(-value)  # type: ignore
    if value == 0:
        return ZO('0')
    digits = []
    while value > 0:
        digits.append(_BASE64_CHARSET[value % 64])
        value //= 64
    return ZO(''.join(reversed(digits)))

def _read_file_metadata(path: str):
    """
    读取文件二进制内容、长度和字节和
    :param path: 文件路径
    :return: (data, length, total_sum)
    """
    with open(path, "rb") as f:
        data = f.read()
        return data, len(data), sum(data)

def zo_basev1(path: str) -> ZO:
    """
    文件的简单哈希（直接使用filehash_256v1的ZO编码）
    :param path: 文件路径
    :return: ZO编码的哈希值
    """
    h = filehash_256v1(path)
    return int_to_zo(h)

def zo1(path: str) -> str:
    """
    文件的增强哈希（v1版本），包含两部分：完整哈希的ZO编码 + 随机采样校验和
    格式：hash_part|sampled_sum_part
    :param path: 文件路径
    :return: 竖线分隔的字符串
    """
    data, length, total = _read_file_metadata(path)
    if length == 0:
        return int_to_zo(0) + "|" + int_to_zo(0)

    fnv_hash = memoryhash_256v2(data)
    part1 = int_to_zo(fnv_hash)

    # 使用长度、总和和哈希值作为种子，保证确定性
    seed = hash((length, total, fnv_hash)) & 0xFFFFFFFF
    rng = random.Random(seed)

    k = rng.randint(1, 128)
    sampled_sum = 0
    for _ in range(k):
        idx = rng.randint(0, length - 1)
        sampled_sum += data[idx]

    part2 = int_to_zo(sampled_sum)
    return f"{part1}|{part2}"

if __name__ == "__main__":
    import sys
    file_path = sys.argv[1]
    result = zo1(file_path)
    print(f"ZO1 value for file {file_path}: {result}")