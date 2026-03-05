import pickle
import traceback
from dataclasses import asdict

from ...schema.table_schema import CellDataConfig, TableDataConfig
from .style_resolver import get_style
from .value_format_resolver import get_value


def convert_to_json_data(self):
    try:
        with open(self.pickle_path, "rb") as f:
            data = pickle.load(f)

        columns = list(data.keys())
        num_rows = len(data[columns[0]])
        style_settings = getattr(self, "style_settings", {})
        value_format_settings = getattr(self, "value_format_settings", {})

        cell_data = []

        # Header row
        header_row = [
            CellDataConfig(
                row=0,
                col=col_idx,
                value=get_value(
                    value_format_settings=value_format_settings,
                    row=0,
                    col=col_idx,
                    value=self.column_names.get(col_name, col_name)
                ),
                style=get_style(
                    style_settings=style_settings,
                    row=0,
                    col=col_idx,
                    value=self.column_names.get(col_name, col_name)
                )
            )
            for col_idx, col_name in enumerate(columns)
        ]
        cell_data.append(header_row)

        # Data rows
        for data_row_idx in range(num_rows):
            data_row = [
                CellDataConfig(
                    row=data_row_idx + 1,
                    col=col_idx,
                    value=get_value(
                        value_format_settings=value_format_settings,
                        row=data_row_idx + 1,
                        col=col_idx,
                        value=data[col_name][data_row_idx]
                    ),
                    style=get_style(
                        style_settings=style_settings,
                        row=data_row_idx + 1,
                        col=col_idx,
                        value=data[col_name][data_row_idx]
                    )
                )
                for col_idx, col_name in enumerate(columns)
            ]
            cell_data.append(data_row)

        table_config = TableDataConfig(
            cell_data=cell_data,
            row_count=len(cell_data),
            col_count=len(columns)
        )

        return asdict(table_config)

    except Exception as e:
        return {
            "error": f"读取数据时发生错误: {str(e)}",
            "traceback": traceback.format_exc(),
            "status": "read_error"
        }
