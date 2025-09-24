from dataclasses import dataclass
from numpy.typing import NDArray
from typing import Any, Iterator


@dataclass
class Format:
    intended_names:list[str]
    search_names:list[list[str]]
    intended_types:list[type]
    use_filter:bool = False
    intended_indexs:list[int] = None
    key_indexs:list[int] = None
    found_names:list[str] = None



@dataclass
class BatchData: 
    data: NDArray[Any]
    rows: int
    valid:bool = True

@dataclass
class File:
    data: Iterator[BatchData]
    rows: int
    file: int = -1
    subfile: int = -1
    valid:bool = True