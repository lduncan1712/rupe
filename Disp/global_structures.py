from dataclasses import dataclass
from numpy.typing import NDArray
from typing import Any, Iterator


@dataclass
class Format:
    intended_names:list[list[str]]
    intended_types:list[tuple[str,type]]
    use_filter:bool = False


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