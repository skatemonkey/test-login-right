import pickle
import traceback
from dataclasses import asdict

from ...models.table_model import CellDataConfig, TableDataConfig


def convert_to_json_data(self):
    try:
        with open(self.pickle_path, "rb") as f:
            data = pickle.load(f)

        columns = list(data.keys())
        num_rows = len(data[columns[0]])

        cell_data = []

        # Header row
        header_row = [
            CellDataConfig(
                row=0,
                col=col_idx,
                value=self.columnNames.get(col_name, col_name),
                style=1
            )
            for col_idx, col_name in enumerate(columns)
        ]
        cell_data.append(header_row)

        # Data rows
        for row_idx in range(num_rows):
            data_row = [
                CellDataConfig(
                    row=row_idx + 1,
                    col=col_idx,
                    value=str(data[col_name][row_idx]),
                    style=2
                )
                for col_idx, col_name in enumerate(columns)
            ]
            cell_data.append(data_row)

        table_config = TableDataConfig(
            cellData=cell_data,
            rowCount=len(cell_data),
            colCount=len(columns)
        )

        return asdict(table_config)

    except Exception as e:
        return {
            "error": f"读取数据时发生错误: {str(e)}",
            "traceback": traceback.format_exc(),
            "status": "read_error"
        }
