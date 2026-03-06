from dataclasses import asdict
import pickle
import traceback

from app.module.table_display.schema.table_schema import CellLayoutConfig, TableLayoutConfig


def convert_to_json_layout(self):
    try:
        with open(self.pickle_path, "rb") as f:
            data = pickle.load(f)

        rows = []

        # Flatten nested structure and track spans
        for model in data["models"]:
            model_start = len(rows)
            for feature in model["features"]:
                feature_start = len(rows)
                for task in feature["tasks"]:
                    rows.append({
                        "model_span": None,
                        "feature_span": None
                    })
                for r in range(feature_start, len(rows)):
                    rows[r]["feature_span"] = (feature_start, len(rows) - feature_start)
            for r in range(model_start, len(rows)):
                rows[r]["model_span"] = (model_start, len(rows) - model_start)

        row_count = len(rows)
        col_count = 4

        cell_layout = []

        for r, row in enumerate(rows):
            layout_row = []

            model_start, model_span = row["model_span"]
            if r == model_start:
                layout_row.append(CellLayoutConfig(r, 0, rowSpan=model_span))

            feature_start, feature_span = row["feature_span"]
            if r == feature_start:
                layout_row.append(CellLayoutConfig(r, 1, rowSpan=feature_span))

            layout_row.append(CellLayoutConfig(r, 2))

            if r == feature_start:
                layout_row.append(CellLayoutConfig(r, 3, rowSpan=feature_span))

            cell_layout.append(layout_row)

        table_layout = TableLayoutConfig(
            cellLayout=cell_layout,
            rowCount=row_count,
            colCount=col_count
        )

        return asdict(table_layout)

    except Exception as e:
        return {
            "error": f"Error reading layout: {str(e)}",
            "traceback": traceback.format_exc(),
            "status": "read_error"
        }
