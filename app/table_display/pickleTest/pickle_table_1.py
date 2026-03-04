import pickle
import time

# Hardcoded cell data
table_data: dict[str, list] = {
    "instrument": ["ETHUSDT", "BCHUSDT", "PNUTUSDT"],
    "bboSpread": [6, 6, 0],
    "midPriceSpread": [6, 6, 0],
}

pickle_path = "/Users/user/hub/dev/test/output/table_1.pkl"
counter = 0

while True:
    # Update one cell (bboSpread for BCHUSDT, index 1)
    table_data["bboSpread"][1] = counter

    with open(pickle_path, "wb") as f:
        pickle.dump(table_data, f)

    print(f"Updated bboSpread[1] to {counter}, saved to {pickle_path}")

    counter += 1
    time.sleep(3)
