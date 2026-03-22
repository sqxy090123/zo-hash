"""
DY哈希模块
基于文件内容的伪随机位点采样，生成唯一指纹
"""

import random
from ._hash import filehash_256v1
from ._zo import int_to_zo

def int_to_dy1(value: int) -> str:
    """将整数转换为 DY 编码（复用 ZO 编码规则）"""
    return int_to_zo(value)

def dy1(path: str) -> str:
    """
    生成文件的 DY1 指纹
    算法：
        1. 用文件哈希值作为随机种子，随机选取一个起始位点。
        2. 从该位点开始取16个字节作为新的随机种子，生成下一个位点。
        3. 重复步骤2，直到遇到已访问过的位点或达到256次。
        4. 将所有访问过的位点对应的字节值，通过一个伪随机变换合并成一个整数，
           最终用 DY 编码返回。
    :param path: 文件路径
    :return: DY1 编码字符串
    """
    # 读取文件内容（小文件直接加载到内存）
    with open(path, 'rb') as f:
        data = f.read()
    length = len(data)
    if length == 0:
        return int_to_dy1(0)

    # 1. 用文件哈希作为随机种子
    seed_val = filehash_256v1(path)
    rng = random.Random(seed_val)

    # 2. 随机选取起始位点
    pos = rng.randint(0, length - 1)

    visited = set()
    positions = []

    # 3. 循环采样
    for _ in range(256):
        if pos in visited:
            break
        visited.add(pos)
        positions.append(pos)

        # 从当前位点取16个字节作为新种子（如果不够则循环读取）
        seed_bytes = bytearray()
        idx = pos
        for _ in range(16):
            seed_bytes.append(data[idx % length])
            idx += 1
        new_seed = int.from_bytes(seed_bytes, 'little')
        rng = random.Random(new_seed)
        pos = rng.randint(0, length - 1)

    # 4. 合并位点对应的字节值，通过伪随机变换
    result = 0
    for p in positions:
        byte_val = data[p]
        # 伪随机变换（固定参数，保证确定性）
        transformed = (byte_val * 0x9E3779B97F4A7C15) ^ 0x1234567890ABCDEF
        transformed &= 0xFFFFFFFFFFFFFFFF  # 保持64位
        result ^= transformed  # 使用异或合并
        # 轻微扰动，增加非线性
        result = (result << 3) | (result >> 61)
        result &= 0xFFFFFFFFFFFFFFFF

    return int_to_dy1(result)