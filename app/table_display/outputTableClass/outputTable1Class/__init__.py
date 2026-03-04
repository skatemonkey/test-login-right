class OutputTable1:
    def __init__(self, ):
        super().__init__()
        self.pickle_path = "/Users/user/hub/dev/test/output/table_1.pkl"
        self.tableSn = 1
        self.columnNames = {
            "instrument": "交易品种",
            "bboSpread": "CW Spread(个ticker)",
            "midPriceSpread": "CW中间价-BN中间价的绝对值(个ticker)",

        }
        self.totalTableTitleRows = 1
        self.columnDisplayOrder = ("交易品种", "CW Spread(个ticker)", "CW中间价-BN中间价的绝对值(个ticker)",)
        self.tableTitle = "做市品种Spread监控"

    from ..shared.convert_to_json_data import convert_to_json_data
    from ..shared.convert_to_json_layout import convert_to_json_layout
