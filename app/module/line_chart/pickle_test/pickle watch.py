import pickle
import time
from datetime import datetime

pickle_path = "/Users/user/hub/dev/test/output/line_chart_1.pkl"

while True:
    try:
        with open(pickle_path, "rb") as f:
            data = pickle.load(f)

        if data:
            latest = data[-1]
            ts = datetime.fromtimestamp(latest["timestamp"])

            print("\033c", end="")  # clear terminal
            print(f"Total rows: {len(data)}")
            print("Latest row:")
            print(ts, latest)

        else:
            print("No data yet")

    except Exception as e:
        print("Waiting for pickle file...", e)

    time.sleep(2)