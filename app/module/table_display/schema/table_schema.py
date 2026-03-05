# table_models.py
from dataclasses import dataclass, field


@dataclass
class CellLayoutConfig:
    row: int
    col: int
    row_span: int = 1
    col_span: int = 1

@dataclass
class TableLayoutConfig:
    cell_layout: list[list[CellLayoutConfig]] = field(default_factory=list)
    row_count: int = 0
    col_count: int = 0




@dataclass
class CellDataConfig:
    row: int
    col: int
    value: str
    style: int = 0

@dataclass
class TableDataConfig:
    cell_data: list[list[CellDataConfig]] = field(default_factory=list)
    row_count: int = 0
    col_count: int = 0