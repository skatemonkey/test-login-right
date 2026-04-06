import importlib.util
from pathlib import Path
import unittest
from unittest.mock import Mock, call, patch

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "app/module/line_chart/pickle_test/long_running_program_demo.py"
)
SPEC = importlib.util.spec_from_file_location("line_chart_1_under_test", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load module from {MODULE_PATH}")
line_chart_1 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(line_chart_1)


class StopLoop(Exception):
    pass


class LineChart1TestCase(unittest.TestCase):
    def test_series_names_remain_pinned_to_original_series(self):
        self.assertEqual(line_chart_1.SERIES_NAMES, ("cpu", "network", "memory"))
        self.assertEqual(line_chart_1.history_key("cpu"), "ts:line_chart:cpu")

    def test_create_sample_has_expected_shape_and_ranges(self):
        sample = line_chart_1.create_sample(1234567890)

        self.assertEqual(sample["timestamp"], 1234567890)
        self.assertEqual(set(sample), {"timestamp", "cpu", "network", "memory"})
        self.assertGreaterEqual(sample["cpu"], 10)
        self.assertLessEqual(sample["cpu"], 90)
        self.assertGreaterEqual(sample["network"], 100)
        self.assertLessEqual(sample["network"], 1000)
        self.assertGreaterEqual(sample["memory"], 20)
        self.assertLessEqual(sample["memory"], 95)

    def test_run_once_writes_sample_to_redis_timeseries(self):
        redis_client = Mock()
        ts_client = redis_client.ts.return_value
        now = 1700000000000

        with patch.object(
            line_chart_1.random,
            "uniform",
            side_effect=[12.345, 456.789, 78.901],
        ):
            sample, removed_count = line_chart_1.run_once(redis_client, now=now)

        expected_sample = {
            "timestamp": now,
            "cpu": 12.35,
            "network": 456.79,
            "memory": 78.9,
        }
        self.assertEqual(sample, expected_sample)
        self.assertEqual(removed_count, 0)

        self.assertEqual(
            ts_client.create.call_args_list,
            [
                call(
                    line_chart_1.history_key("cpu"),
                    retention_msecs=line_chart_1.RETENTION_MILLISECONDS,
                ),
                call(
                    line_chart_1.history_key("network"),
                    retention_msecs=line_chart_1.RETENTION_MILLISECONDS,
                ),
                call(
                    line_chart_1.history_key("memory"),
                    retention_msecs=line_chart_1.RETENTION_MILLISECONDS,
                ),
            ],
        )
        self.assertEqual(
            ts_client.add.call_args_list,
            [
                call(
                    line_chart_1.history_key("cpu"),
                    now,
                    12.35,
                    duplicate_policy="LAST",
                ),
                call(
                    line_chart_1.history_key("network"),
                    now,
                    456.79,
                    duplicate_policy="LAST",
                ),
                call(
                    line_chart_1.history_key("memory"),
                    now,
                    78.9,
                    duplicate_policy="LAST",
                ),
            ],
        )
        self.assertEqual(
            redis_client.publish.call_args_list,
            [
                call(
                    line_chart_1.LIVE_UPDATES_CHANNEL,
                    line_chart_1.serialize_live_update("cpu", now, 12.35),
                ),
                call(
                    line_chart_1.LIVE_UPDATES_CHANNEL,
                    line_chart_1.serialize_live_update("network", now, 456.79),
                ),
                call(
                    line_chart_1.LIVE_UPDATES_CHANNEL,
                    line_chart_1.serialize_live_update("memory", now, 78.9),
                ),
            ],
        )
        redis_client.zremrangebyscore.assert_not_called()

    def test_reset_and_seed_history_defaults_to_five_hours(self):
        redis_client = Mock()
        ts_client = redis_client.ts.return_value

        def make_sample(timestamp):
            return {
                "timestamp": timestamp,
                "cpu": 1.0,
                "network": 2.0,
                "memory": 3.0,
            }

        with patch.object(line_chart_1, "create_sample", side_effect=make_sample):
            seeded_count = line_chart_1.reset_and_seed_history(redis_client, now=18_000_000)

        expected_count = (
            line_chart_1.INITIAL_HISTORY_SECONDS // line_chart_1.SAMPLE_INTERVAL_SECONDS
        ) + 1
        self.assertEqual(line_chart_1.INITIAL_HISTORY_SECONDS, 5 * 60 * 60)
        self.assertEqual(seeded_count, expected_count)
        redis_client.delete.assert_called_once_with(
            *(line_chart_1.history_key(series_name) for series_name in line_chart_1.SERIES_NAMES),
        )
        self.assertEqual(
            ts_client.create.call_args_list,
            [
                call(
                    line_chart_1.history_key("cpu"),
                    retention_msecs=line_chart_1.RETENTION_MILLISECONDS,
                ),
                call(
                    line_chart_1.history_key("network"),
                    retention_msecs=line_chart_1.RETENTION_MILLISECONDS,
                ),
                call(
                    line_chart_1.history_key("memory"),
                    retention_msecs=line_chart_1.RETENTION_MILLISECONDS,
                ),
            ],
        )
        madd_rows = ts_client.madd.call_args.args[0]
        self.assertEqual(madd_rows[0][1], 0)
        self.assertEqual(madd_rows[-1][1], 18_000_000)
        self.assertEqual(len(madd_rows), expected_count * len(line_chart_1.SERIES_NAMES))

        redis_client.publish.assert_not_called()

    def test_reset_and_seed_history_clears_key_and_stores_expected_window(self):
        redis_client = Mock()
        ts_client = redis_client.ts.return_value

        def make_sample(timestamp):
            return {
                "timestamp": timestamp,
                "cpu": float(timestamp),
                "network": float(timestamp) + 1,
                "memory": float(timestamp) + 2,
            }

        with patch.object(line_chart_1, "create_sample", side_effect=make_sample):
            seeded_count = line_chart_1.reset_and_seed_history(
                redis_client,
                now=100_000,
                history_seconds=10,
                interval_seconds=5,
            )

        self.assertEqual(seeded_count, 3)
        redis_client.delete.assert_called_once_with(
            *(line_chart_1.history_key(series_name) for series_name in line_chart_1.SERIES_NAMES),
        )
        self.assertEqual(
            ts_client.create.call_args_list,
            [
                call(
                    line_chart_1.history_key("cpu"),
                    retention_msecs=line_chart_1.RETENTION_MILLISECONDS,
                ),
                call(
                    line_chart_1.history_key("network"),
                    retention_msecs=line_chart_1.RETENTION_MILLISECONDS,
                ),
                call(
                    line_chart_1.history_key("memory"),
                    retention_msecs=line_chart_1.RETENTION_MILLISECONDS,
                ),
            ],
        )
        self.assertEqual(
            ts_client.madd.call_args_list,
            [
                call(
                    [
                        (line_chart_1.history_key("cpu"), 90_000, 90_000.0),
                        (line_chart_1.history_key("network"), 90_000, 90_001.0),
                        (line_chart_1.history_key("memory"), 90_000, 90_002.0),
                        (line_chart_1.history_key("cpu"), 95_000, 95_000.0),
                        (line_chart_1.history_key("network"), 95_000, 95_001.0),
                        (line_chart_1.history_key("memory"), 95_000, 95_002.0),
                        (line_chart_1.history_key("cpu"), 100_000, 100_000.0),
                        (line_chart_1.history_key("network"), 100_000, 100_001.0),
                        (line_chart_1.history_key("memory"), 100_000, 100_002.0),
                    ]
                ),
            ],
        )
        ts_client.add.assert_not_called()
        redis_client.publish.assert_not_called()

    def test_run_forever_runs_one_iteration_before_sleep_stops(self):
        redis_client = Mock()

        def stop(_interval):
            raise StopLoop()

        with patch.object(line_chart_1, "run_once") as run_once:
            with self.assertRaises(StopLoop):
                line_chart_1.run_forever(
                    redis_client,
                    sleep=stop,
                    time_func=lambda: 123,
                )

        run_once.assert_called_once_with(redis_client, now=123000)

    def test_run_forever_can_sleep_before_first_iteration(self):
        redis_client = Mock()
        sleep = Mock(side_effect=[None, StopLoop()])

        with patch.object(line_chart_1, "run_once") as run_once:
            with self.assertRaises(StopLoop):
                line_chart_1.run_forever(
                    redis_client,
                    interval_seconds=5,
                    sleep=sleep,
                    time_func=lambda: 456,
                    sleep_first=True,
                )

        sleep.assert_any_call(5)
        run_once.assert_called_once_with(redis_client, now=456000)


if __name__ == "__main__":
    unittest.main()
