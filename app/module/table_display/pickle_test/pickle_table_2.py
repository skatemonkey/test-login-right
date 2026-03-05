import pickle
import random
import time

# Initial data
table_data: dict[str, list] = {
    "instrument": ["ETHUSDT", "BCHUSDT", "PNUTUSDT"],
    "bbo_spread": [6, 6, 0],
    "mid_price_spread": [6, 6, 0],
}

pickle_path = "/Users/user/hub/dev/test/output/table_2.pkl"
counter = 0

# Pool of instruments to add
available_instruments = ["BTCUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT"]


def add_row():
    """Add a random new row"""
    if available_instruments:
        new_instrument = random.choice(available_instruments)
        available_instruments.remove(new_instrument)
        table_data["instrument"].append(new_instrument)
        table_data["bbo_spread"].append(random.randint(0, 10))
        table_data["mid_price_spread"].append(random.randint(0, 10))
        print(f"  Added row: {new_instrument}")


def remove_row():
    """Remove a random row (keep at least 1)"""
    if len(table_data["instrument"]) > 1:
        idx = random.randint(0, len(table_data["instrument"]) - 1)
        removed = table_data["instrument"].pop(idx)
        table_data["bbo_spread"].pop(idx)
        table_data["mid_price_spread"].pop(idx)
        available_instruments.append(removed)  # Return to pool
        print(f"  Removed row: {removed}")


while True:
    # Randomly add, remove, or do nothing
    action = random.choice(["add", "remove"])

    if action == "add":
        add_row()
    elif action == "remove":
        remove_row()

    # Update a random bbo_spread value
    if table_data["bbo_spread"]:
        idx = random.randint(0, len(table_data["bbo_spread"]) - 1)
        table_data["bbo_spread"][idx] = counter

    with open(pickle_path, "wb") as f:
        pickle.dump(table_data, f)

    print(f"Tick {counter}: {len(table_data['instrument'])} rows | {table_data['instrument']}")

    counter += 1
    time.sleep(3)