import traceback
from dataclasses import asdict

from ...schema.table_schema import TableDataConfig, CellDataConfig


def convert_to_json_data(self):
    try:
        response = TableDataConfig(
            cell_data=[
                [CellDataConfig(0, 0, "1", 1), CellDataConfig(0, 1, "2", 1)],
                [CellDataConfig(1, 0, "3", 1), CellDataConfig(1, 1, "4", 1)],
                [CellDataConfig(2, 0, "5", 1)],
                [CellDataConfig(3, 0, "6", 1), CellDataConfig(3, 1, "7", 1)],
                [CellDataConfig(4, 0, "8", 1)],
                [CellDataConfig(5, 0, "9", 1)],
                [CellDataConfig(6, 0, "10", 1)],
                [CellDataConfig(7, 0, "11", 1), CellDataConfig(7, 1, "13", 1)],
                [CellDataConfig(8, 0, "12", 1)],
            ],
            row_count=9,
            col_count=4
        )

        return asdict(response)  # Convert dataclass to dict

    except Exception as e:
        return {
            "error": f"读取数据时发生错误: {str(e)}",
            "traceback": traceback.format_exc(),
            "status": "read_error"
        }
