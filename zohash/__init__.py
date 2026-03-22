"""
# ZO-Hash 模块
## 提供基于海绵结构的256位哈希算法，以及ZO编码的哈希表示。
## 支持内存数据和文件的哈希计算。
usage:
```
>>> import zohash
>>> zohash.dy512("C:/path/to/your/file") # on win
'2t4ggPh.IVQqpZhFO.43TYYlF3pNSV9XXlm7Cuhai.Fsgr2Xwn495j402JJQv7EY1Ypg8FJWCWeLsjpxXlAZ6h'
>>> zohash.dy512("/path/to/your/file") # on linux
'2t4ggPh.IVQqpZhFO.43TYYlF3pNSV9XXlm7Cuhai.Fsgr2Xwn495j402JJQv7EY1Ypg8FJWCWeLsjpxXlAZ6h'
```
"""


from ._hash import filehash_256v1, memoryhash_256v2
from . import _dyhash as dyhash
from . import _zo as zohash
"""
from ._zo import zo_basev1, zo1, zo2
from ._dyhash import dy1, dy64, dy128, dy256, dy512
"""


__all__ = [
    "zohash",
    "dyhash"
]