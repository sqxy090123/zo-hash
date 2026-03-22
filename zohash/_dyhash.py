"""
DY哈希模块
包含原 dy1（保留原逻辑）和新版 dy64/dy128/dy256/dy512（采用流式随机采样，已修复全零 bug）
"""

import random
import os
from ._hash import filehash_256v1
from ._zo import int_to_zo

# ==================== 原 dy1 保持不变 ====================
def int_to_dy1(value: int) -> str:
    """将整数转换为 DY 编码（复用 ZO 编码规则）"""
    return int_to_zo(value)

def dy1(path: str) -> str:
    """
    生成文件的 DY1 指纹（原版，保留）
    一次性读入整个文件，最多采样256个不重复位点，输出64位。
    """
    with open(path, 'rb') as f:
        data = f.read()
    length = len(data)
    if length == 0:
        return int_to_dy1(0)

    seed_val = filehash_256v1(path)
    rng = random.Random(seed_val)

    pos = rng.randint(0, length - 1)
    visited = set()
    positions = []

    for _ in range(256):
        if pos in visited:
            break
        visited.add(pos)
        positions.append(pos)

        seed_bytes = bytearray()
        idx = pos
        for _ in range(16):
            seed_bytes.append(data[idx % length])
            idx += 1
        new_seed = int.from_bytes(seed_bytes, 'little')
        rng = random.Random(new_seed)
        pos = rng.randint(0, length - 1)

    result = 0
    for p in positions:
        byte_val = data[p]
        transformed = (byte_val * 0x9E3779B97F4A7C15) ^ 0x1234567890ABCDEF
        transformed &= 0xFFFFFFFFFFFFFFFF
        result ^= transformed
        result = (result << 3) | (result >> 61)
        result &= 0xFFFFFFFFFFFFFFFF

    return int_to_dy1(result)


# ==================== 新版流式动态长度函数（已修复全零 bug） ====================
def _dy_generic(path: str, output_bits: int, max_steps: int = 256, max_len: int = 64) -> str:
    """
    通用 DY 生成函数（修复版）
    :param path: 文件路径
    :param output_bits: 输出位数（64/128/256/512）
    :param max_steps: 最大迭代步数（默认256）
    :param max_len: 每次读取的最大字节数（默认64）
    :return: ZO 编码字符串
    """
    # 获取文件大小
    file_size = os.path.getsize(path)
    if file_size == 0:
        return int_to_zo(0)

    # 初始种子：文件哈希（256位）
    seed_val = filehash_256v1(path)
    rng = random.Random(seed_val)

    # 使用非零初始值，避免全零结果
    result = 0x9E3779B97F4A7C15 & ((1 << output_bits) - 1)
    mask = (1 << output_bits) - 1

    with open(path, 'rb') as f:
        for step in range(max_steps):
            # 随机位点
            pos = rng.randint(0, file_size - 1)
            # 随机读取长度（1 ~ max_len）
            length = rng.randint(1, max_len)

            # 从 pos 开始读取 length 个字节（循环读取）
            seed_bytes = bytearray()
            for i in range(length):
                # 计算实际读取位置（循环）
                idx = (pos + i) % file_size
                f.seek(idx)
                b = f.read(1)
                if not b:
                    # 理论上不会发生，因为文件非空
                    continue
                byte_val = b[0]
                seed_bytes.append(byte_val)
                # 合并每个字节到结果
                transformed = (byte_val * 0x9E3779B97F4A7C15) ^ 0x1234567890ABCDEF
                transformed &= 0xFFFFFFFFFFFFFFFF
                result ^= transformed
                # 增加步数扰动，增强非线性
                result ^= (step + 1)
                # 循环左移 3 位（按 output_bits 宽度）
                result = ((result << 3) | (result >> (output_bits - 3))) & mask

            # 使用读取的字节生成新种子（用于下一个位点）
            new_seed = int.from_bytes(seed_bytes, 'little')
            rng = random.Random(new_seed)

    return int_to_zo(result)


def dy64(path: str) -> str:
    """64 位 DY 指纹，流式随机采样，输出 64 位（修复版）"""
    return _dy_generic(path, 64)


def dy128(path: str) -> str:
    """128 位 DY 指纹，流式随机采样，输出 128 位（修复版）"""
    return _dy_generic(path, 128)


def dy256(path: str) -> str:
    """256 位 DY 指纹，流式随机采样，输出 256 位（修复版）"""
    return _dy_generic(path, 256)


def dy512(path: str) -> str:
    """512 位 DY 指纹，流式随机采样，输出 512 位（修复版）"""
    return _dy_generic(path, 512)