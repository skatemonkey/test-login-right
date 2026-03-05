import pickle
import random
import time

# Hardcoded cell data
table_data: dict[str, list] = {
    "instrument": ["ETHUSDT", "BCHUSDT", "PNUTUSDT"],
    "bbo_spread": [6, 0, 18],
    "mid_price_spread": [12, 5, 0],
}

pickle_path = "/Users/user/hub/dev/test/output/table_1.pkl"


def random_spread_value() -> int:
    roll = random.random()

    # Split evenly into 3 outcomes.
    if roll < (1 / 3):
        return random.randint(0, 10)
    if roll < (2 / 3):
        return random.randint(11, 25)

    # Final third produces a large spike > 1000.
    return random.randint(1001, 2000)

while True:
    table_data["bbo_spread"] = [
        random_spread_value() for _ in table_data["bbo_spread"]
    ]
    table_data["mid_price_spread"] = [
        random_spread_value() for _ in table_data["mid_price_spread"]
    ]

    with open(pickle_path, "wb") as f:
        pickle.dump(table_data, f)

    print(
        f"Updated bbo_spread={table_data['bbo_spread']}, "
        f"mid_price_spread={table_data['mid_price_spread']}, saved to {pickle_path}"
    )

    time.sleep(3)
