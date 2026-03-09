from dataclasses import asdict


def convert_to_json_layout(self):
    try:
        # Convert dataclass to dict
        return asdict(self.layout_config)
    except Exception as e:
        return {
            "error": f"读取布局时发生错误: {str(e)}",
            "status": "read_error"
        }
