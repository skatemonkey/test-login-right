import pickle
import traceback
from dataclasses import asdict

from ...schema.table_schema import CellLayoutConfig, TableLayoutConfig


def convert_to_json_layout(self):
    try:
        with open(self.pickle_path, "rb") as f:
            data = pickle.load(f)

        columns = list(data.keys())
        col_count = len(columns)
        row_count = len(data[columns[0]]) + 1  # +1 for header

        cell_layout = [
            [
                CellLayoutConfig(
                    row=row_idx,
                    col=col_idx,
                    row_span=1,
                    col_span=1
                )
                for col_idx in range(col_count)
            ]
            for row_idx in range(row_count)
        ]

        table_layout = TableLayoutConfig(
            cell_layout=cell_layout,
            row_count=row_count,
            col_count=col_count
        )

        return asdict(table_layout)

    except Exception as e:
        return {
            "error": f"读取布局时发生错误: {str(e)}",
            "traceback": traceback.format_exc(),
            "status": "read_error"
        }
