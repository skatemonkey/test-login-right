# table_models.py
from dataclasses import dataclass, field


@dataclass
class CellLayoutConfig:
    row: int
    col: int
    rowSpan: int = 1
    colSpan: int = 1

@dataclass
class TableLayoutConfig:
    cellLayout: list[list[CellLayoutConfig]] = field(default_factory=list)
    rowCount: int = 0
    colCount: int = 0




@dataclass
class CellDataConfig:
    row: int
    col: int
    value: str
    style: int = 0

@dataclass
class TableDataConfig:
    cellData: list[list[CellDataConfig]] = field(default_factory=list)
    rowCount: int = 0
    colCount: int = 0
