from ...schema.table_schema import TableLayoutConfig, CellLayoutConfig


class OutputTable4:
    def __init__(self):
        super().__init__()
        self.pickle_path = "/Users/user/hub/dev/test/output/table_4.pkl"

    from ..shared.convert_to_json_layout_4 import convert_to_json_layout
    from ..shared.convert_to_json_data_4 import convert_to_json_data
