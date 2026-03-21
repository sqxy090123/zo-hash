"""
ZO编码及基于海绵哈希的增强哈希功能
提供将整数转换为自定义base64字符串的函数，以及三种文件哈希方法：
- zo_basev1: 直接使用filehash_256v1哈希的base64表示
- zo1: 在哈希基础上增加随机采样校验
- zo2: 在zo1基础上增加文件特征哈希（前、中、后各512字节）作为附加校验
"""

import random
from ._hash import filehash_256v1, Sponge256

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

def _file_length_and_sum(path: str, chunk_size: int = 65536):
    """
    流式计算文件长度和字节和
    :param path: 文件路径
    :param chunk_size: 读取块大小
    :return: (length, total_sum)
    """
    length = 0
    total = 0
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            length += len(chunk)
            total += sum(chunk)
    return length, total

def _file_sample_sum(path: str, indices: list, chunk_size: int = 65536):
    """
    根据索引列表流式计算采样字节和
    :param path: 文件路径
    :param indices: 待采样字节索引列表（已排序）
    :param chunk_size: 读取块大小
    :return: 采样字节值的和
    """
    indices_sorted = sorted(indices)
    sampled_sum = 0
    pos = 0
    idx_ptr = 0
    with open(path, "rb") as f:
        while idx_ptr < len(indices_sorted):
            target = indices_sorted[idx_ptr]
            if pos > target:
                raise RuntimeError("Unexpected state")
            f.seek(target)
            byte = f.read(1)
            if not byte:
                break
            sampled_sum += byte[0]
            pos = target + 1
            idx_ptr += 1
    return sampled_sum

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
    h = filehash_256v1(path)
    length, total = _file_length_and_sum(path)
    if length == 0:
        return int_to_zo(0) + "|" + int_to_zo(0)

    seed = hash((length, total, h)) & 0xFFFFFFFF
    rng = random.Random(seed)
    k = rng.randint(1, 128)

    # 生成随机索引
    indices = [rng.randint(0, length - 1) for _ in range(k)]
    sampled_sum = _file_sample_sum(path, indices)

    return f"{int_to_zo(h)}|{int_to_zo(sampled_sum)}"

def zo2(path: str) -> str:
    """
    文件的增强哈希（v2版本），在zo1基础上增加文件特征哈希（前、中、后各512字节）
    格式：hash_part|feature_part|sampled_sum_part
    :param path: 文件路径
    :return: 竖线分隔的字符串
    """
    h = filehash_256v1(path)
    length, total = _file_length_and_sum(path)
    if length == 0:
        return int_to_zo(0) + "|" + int_to_zo(0) + "|" + int_to_zo(0)

    seed = hash((length, total, h)) & 0xFFFFFFFF
    rng = random.Random(seed)
    k = rng.randint(1, 128)
    indices = [rng.randint(0, length - 1) for _ in range(k)]
    sampled_sum = _file_sample_sum(path, indices)

    # 计算特征哈希（前512字节、中间512字节、后512字节）
    CHUNK_SIZE = 512
    h_start = Sponge256()
    h_mid = Sponge256()
    h_end = Sponge256()

    mid_start = max(0, (length // 2) - CHUNK_SIZE // 2)
    end_start = max(0, length - CHUNK_SIZE)

    with open(path, "rb") as f:
        pos = 0
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            chunk_len = len(chunk)

            # 前部
            if pos < CHUNK_SIZE:
                take = min(chunk_len, CHUNK_SIZE - pos)
                h_start.update(chunk[:take])
            # 中部
            if pos + chunk_len > mid_start and pos < mid_start + CHUNK_SIZE:
                start_off = max(mid_start - pos, 0)
                end_off = min(mid_start + CHUNK_SIZE - pos, chunk_len)
                if start_off < end_off:
                    h_mid.update(chunk[start_off:end_off])
            # 后部
            if pos + chunk_len > end_start and pos < end_start + CHUNK_SIZE:
                start_off = max(end_start - pos, 0)
                end_off = min(end_start + CHUNK_SIZE - pos, chunk_len)
                if start_off < end_off:
                    h_end.update(chunk[start_off:end_off])
            pos += chunk_len

    start_hash = h_start.digest() if CHUNK_SIZE > 0 else 0
    mid_hash = h_mid.digest() if length > CHUNK_SIZE else 0
    end_hash = h_end.digest() if length > CHUNK_SIZE else 0
    feature_int = start_hash ^ mid_hash ^ end_hash

    return f"{int_to_zo(h)}|{int_to_zo(feature_int)}|{int_to_zo(sampled_sum)}"

if __name__ == "__main__":
    import sys
    file_path = sys.argv[1]
    result = zo1(file_path)
    print(f"ZO1 value for file {file_path}: {result}")