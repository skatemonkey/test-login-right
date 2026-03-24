import importlib.util
import json
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

    def test_run_once_writes_sample_and_prunes_old_entries(self):
        redis_client = Mock()
        redis_client.zremrangebyscore.side_effect = [2, 2, 2]
        now = 1700000000

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
        self.assertEqual(removed_count, 6)

        self.assertEqual(
            redis_client.zadd.call_args_list,
            [
                call(
                    line_chart_1.history_key("cpu"),
                    {line_chart_1.serialize_history_point(now, 12.35): now},
                ),
                call(
                    line_chart_1.history_key("network"),
                    {line_chart_1.serialize_history_point(now, 456.79): now},
                ),
                call(
                    line_chart_1.history_key("memory"),
                    {line_chart_1.serialize_history_point(now, 78.9): now},
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

        self.assertEqual(
            redis_client.zremrangebyscore.call_args_list,
            [
                call(
                    line_chart_1.history_key("cpu"),
                    "-inf",
                    now - line_chart_1.RETENTION_SECONDS - 1,
                ),
                call(
                    line_chart_1.history_key("network"),
                    "-inf",
                    now - line_chart_1.RETENTION_SECONDS - 1,
                ),
                call(
                    line_chart_1.history_key("memory"),
                    "-inf",
                    now - line_chart_1.RETENTION_SECONDS - 1,
                ),
            ],
        )

    def test_reset_and_seed_history_defaults_to_five_hours(self):
        redis_client = Mock()

        def make_sample(timestamp):
            return {
                "timestamp": timestamp,
                "cpu": 1.0,
                "network": 2.0,
                "memory": 3.0,
            }

        with patch.object(line_chart_1, "create_sample", side_effect=make_sample):
            seeded_count = line_chart_1.reset_and_seed_history(redis_client, now=18_000)

        expected_count = (
            line_chart_1.INITIAL_HISTORY_SECONDS // line_chart_1.SAMPLE_INTERVAL_SECONDS
        ) + 1
        self.assertEqual(line_chart_1.INITIAL_HISTORY_SECONDS, 5 * 60 * 60)
        self.assertEqual(seeded_count, expected_count)
        redis_client.delete.assert_called_once_with(
            line_chart_1.LEGACY_REDIS_KEY,
            *(line_chart_1.history_key(series_name) for series_name in line_chart_1.SERIES_NAMES),
        )
        self.assertEqual(len(redis_client.zadd.call_args_list), len(line_chart_1.SERIES_NAMES))

        for zadd_call in redis_client.zadd.call_args_list:
            stored_timestamps = sorted(zadd_call.args[1].values())
            self.assertEqual(stored_timestamps[0], 0)
            self.assertEqual(stored_timestamps[-1], 18_000)
        redis_client.publish.assert_not_called()

    def test_reset_and_seed_history_clears_key_and_stores_expected_window(self):
        redis_client = Mock()

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
                now=100,
                history_seconds=10,
                interval_seconds=5,
            )

        self.assertEqual(seeded_count, 3)
        redis_client.delete.assert_called_once_with(
            line_chart_1.LEGACY_REDIS_KEY,
            *(line_chart_1.history_key(series_name) for series_name in line_chart_1.SERIES_NAMES),
        )
        self.assertEqual(len(redis_client.zadd.call_args_list), len(line_chart_1.SERIES_NAMES))

        stored_members_by_key = {
            zadd_call.args[0]: zadd_call.args[1]
            for zadd_call in redis_client.zadd.call_args_list
        }
        expected_points = {
            line_chart_1.history_key("cpu"): [
                {"timestamp": 90, "value": 90.0},
                {"timestamp": 95, "value": 95.0},
                {"timestamp": 100, "value": 100.0},
            ],
            line_chart_1.history_key("network"): [
                {"timestamp": 90, "value": 91.0},
                {"timestamp": 95, "value": 96.0},
                {"timestamp": 100, "value": 101.0},
            ],
            line_chart_1.history_key("memory"): [
                {"timestamp": 90, "value": 92.0},
                {"timestamp": 95, "value": 97.0},
                {"timestamp": 100, "value": 102.0},
            ],
        }

        for key, expected_series_points in expected_points.items():
            stored_members = stored_members_by_key[key]
            self.assertEqual(sorted(stored_members.values()), [90, 95, 100])
            decoded_points = sorted(
                (json.loads(payload) for payload in stored_members),
                key=lambda point: point["timestamp"],
            )
            self.assertEqual(decoded_points, expected_series_points)
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

        run_once.assert_called_once_with(redis_client, now=123)

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
        run_once.assert_called_once_with(redis_client, now=456)


if __name__ == "__main__":
    unittest.main()
