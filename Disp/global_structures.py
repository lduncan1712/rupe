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
    valid:bool = True
    file: int
    subfile: int