"""
自定义海绵结构哈希算法（256位）
状态：512位（8个64位字）
吸收速率：256位（4个字）
容量：256位（4个字）
轮数：12
基于ARX置换，抗可逆性
"""

import sys

STATE_WORDS = 8
RATE_WORDS = 4
CAPACITY_WORDS = 4
WORD_BITS = 64
WORD_MASK = (1 << WORD_BITS) - 1

# 轮常数（黄金分割比小数部分）
ROUND_CONSTANTS = [
    0x9E3779B97F4A7C15, 0xF39CC0605CEDC834, 0x1082276BF3A27251, 0xF86C6A11D0C18E95,
    0x243F6A8885A308D3, 0x13198A2E03707344, 0xA4093822299F31D0, 0x082EFA98EC4E6C89,
    0x452821E638D01377, 0xBE5466CF34E90C6C, 0xC0AC29B7C97C50DD, 0x3F84D5B5B5470917,
]

def rotl(x: int, n: int) -> int:
    """64位循环左移"""
    n &= 63
    return ((x << n) | (x >> (64 - n))) & WORD_MASK

def rotr(x: int, n: int) -> int:
    """64位循环右移"""
    n &= 63
    return ((x >> n) | (x << (64 - n))) & WORD_MASK

def permutation(state: list) -> None:
    """
    对8个64位字进行ARX置换（12轮）
    :param state: 状态列表，原地修改
    """
    for r in range(12):
        # 列混合（异或相邻字）
        for i in range(STATE_WORDS):
            state[i] ^= rotl(state[(i + 1) % STATE_WORDS], 13)
            state[i] ^= rotr(state[(i + 2) % STATE_WORDS], 17)
        # 行混合（加法 + 异或）
        for i in range(STATE_WORDS):
            state[i] = (state[i] + state[(i + 3) % STATE_WORDS]) & WORD_MASK
            state[i] ^= state[(i + 4) % STATE_WORDS]
        # 整体旋转（循环移位状态数组）
        state.append(state.pop(0))
        # 加轮常数（仅影响第一个字）
        state[0] ^= ROUND_CONSTANTS[r % len(ROUND_CONSTANTS)]

class Sponge256:
    """海绵结构哈希，支持流式更新"""
    def __init__(self) -> None:
        self._state = [0] * STATE_WORDS
        self._buffer = bytearray()
        self._total = 0

    def _absorb_block(self, block: bytes) -> None:
        """
        吸收一个速率块（32字节），异或到状态的前RATE_WORDS个字
        :param block: 32字节数据块
        """
        words = [int.from_bytes(block[i*8:(i+1)*8], 'little') for i in range(RATE_WORDS)]
        for i in range(RATE_WORDS):
            self._state[i] ^= words[i]
        permutation(self._state)

    def update(self, data: bytes) -> None:
        """增量更新哈希"""
        self._buffer.extend(data)
        while len(self._buffer) >= 32:
            block = self._buffer[:32]
            self._buffer = self._buffer[32:]
            self._absorb_block(block)
            self._total += 32

    def digest(self) -> int:
        """
        返回256位哈希值（前4个字）
        :return: 整数形式的哈希值
        """
        # 填充：添加0x80和0x00，使剩余数据长度达到32字节的整数倍
        self._buffer.append(0x80)
        while len(self._buffer) % 32 != 0:
            self._buffer.append(0x00)
        if self._buffer:
            self._absorb_block(bytes(self._buffer))
        # 吸收总长度（64位）
        length_block = self._total.to_bytes(8, 'little') + b'\x00' * 24
        self._absorb_block(length_block)
        # 再应用一轮置换
        permutation(self._state)
        # 提取前4个字（256位）
        result = 0
        for i in range(RATE_WORDS):
            result |= (self._state[i] << (64 * i))
        return result

def filehash_256v1(path: str, chunk_size: int = 65536) -> int:
    """
    流式计算文件的256位哈希（v1版本）
    :param path: 文件路径
    :param chunk_size: 读取块大小，默认64KB
    :return: 哈希整数值
    """
    h = Sponge256()
    with open(path, 'rb') as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.digest()

def memoryhash_256v2(data: bytes) -> int:
    """
    计算内存数据的256位哈希（v2版本）
    :param data: 字节数据
    :return: 哈希整数值
    """
    h = Sponge256()
    h.update(data)
    return h.digest()