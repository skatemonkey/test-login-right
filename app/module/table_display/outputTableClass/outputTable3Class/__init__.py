from ...schema.table_schema import TableLayoutConfig, CellLayoutConfig


class OutputTable3:
    def __init__(self):
        super().__init__()
        self.pickle_path = "/Users/user/hub/dev/test/output/table_2.pkl"
        self.layout_config = TableLayoutConfig(
            cellLayout=[
                [CellLayoutConfig(0, 0, 1, 2), CellLayoutConfig(0, 1, 2, 1)],
                [CellLayoutConfig(1, 0, 1, 1), CellLayoutConfig(1, 1, 1, 1)],
                [CellLayoutConfig(2, 0, 1, 3)],
                [CellLayoutConfig(3, 0, 3, 1), CellLayoutConfig(3, 1, 1, 2)],
                [CellLayoutConfig(4, 0, 1, 2)],
                [CellLayoutConfig(5, 0, 1, 2)],
                [CellLayoutConfig(6, 0, 1, 2)],
                [CellLayoutConfig(7, 0, 1, 1), CellLayoutConfig(7, 1, 2, 3)],
                [CellLayoutConfig(8, 0, 1, 1)],
            ],
            rowCount=9,
            colCount=4
        )

    from ..shared.convert_to_json_layout_3 import convert_to_json_layout
    from ..shared.convert_to_json_data_3 import convert_to_json_data
