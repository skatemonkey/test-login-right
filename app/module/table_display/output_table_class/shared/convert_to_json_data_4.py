from dataclasses import asdict
import pickle
import traceback

from app.module.table_display.schema.table_schema import CellDataConfig, TableDataConfig


def convert_to_json_data(self):
    try:
        with open(self.pickle_path, "rb") as f:
            data = pickle.load(f)

        cell_data = []
        row_idx = 0

        for model in data["models"]:
            for feature in model["features"]:
                for task in feature["tasks"]:
                    data_row = [
                        CellDataConfig(row_idx, 0, model["name"]),
                        CellDataConfig(row_idx, 1, feature["name"]),
                        CellDataConfig(row_idx, 2, task),
                        CellDataConfig(row_idx, 3, feature["owner"] or "")
                    ]
                    cell_data.append(data_row)
                    row_idx += 1

        table_data = TableDataConfig(
            cellData=cell_data,
            rowCount=row_idx,
            colCount=4
        )

        return asdict(table_data)

    except Exception as e:
        return {
            "error": f"Error reading data: {str(e)}",
            "traceback": traceback.format_exc(),
            "status": "read_error"
        }
