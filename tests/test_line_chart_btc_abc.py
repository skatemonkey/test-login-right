import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import Mock, call, patch

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "app/module/line_chart/pickle_test/long_running_program_btc_abc.py"
)
SPEC = importlib.util.spec_from_file_location("line_chart_btc_abc_under_test", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load module from {MODULE_PATH}")
line_chart_btc_abc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(line_chart_btc_abc)


class StopLoop(Exception):
    pass


class LineChartBtcAbcTestCase(unittest.TestCase):
    def test_create_sample_has_expected_shape_and_ranges(self):
        sample = line_chart_btc_abc.create_sample(1234567890)

        self.assertEqual(sample["timestamp"], 1234567890)
        self.assertEqual(set(sample), {"timestamp", "btc", "abc"})
        self.assertGreaterEqual(sample["btc"], 30_000)
        self.assertLessEqual(sample["btc"], 90_000)
        self.assertLess(sample["abc"], sample["btc"])
        self.assertGreaterEqual(sample["btc"] - sample["abc"], 100)
        self.assertLessEqual(sample["btc"] - sample["abc"], 1_500)

    def test_run_once_writes_sample_and_prunes_old_entries(self):
        redis_client = Mock()
        redis_client.zremrangebyscore.side_effect = [2, 2]
        now = 1700000000

        with patch.object(
            line_chart_btc_abc.random,
            "uniform",
            side_effect=[42_123.456, 321.111],
        ):
            sample, removed_count = line_chart_btc_abc.run_once(redis_client, now=now)

        expected_sample = {
            "timestamp": now,
            "btc": 42123.46,
            "abc": 41802.35,
        }
        self.assertEqual(sample, expected_sample)
        self.assertEqual(removed_count, 4)

        self.assertEqual(
            redis_client.zadd.call_args_list,
            [
                call(
                    line_chart_btc_abc.history_key("btc"),
                    {line_chart_btc_abc.serialize_history_point(now, 42123.46): now},
                ),
                call(
                    line_chart_btc_abc.history_key("abc"),
                    {line_chart_btc_abc.serialize_history_point(now, 41802.35): now},
                ),
            ],
        )
        self.assertEqual(
            redis_client.publish.call_args_list,
            [
                call(
                    line_chart_btc_abc.LIVE_UPDATES_CHANNEL,
                    line_chart_btc_abc.serialize_live_update("btc", now, 42123.46),
                ),
                call(
                    line_chart_btc_abc.LIVE_UPDATES_CHANNEL,
                    line_chart_btc_abc.serialize_live_update("abc", now, 41802.35),
                ),
            ],
        )
        self.assertEqual(
            redis_client.zremrangebyscore.call_args_list,
            [
                call(
                    line_chart_btc_abc.history_key("btc"),
                    "-inf",
                    now - line_chart_btc_abc.RETENTION_SECONDS - 1,
                ),
                call(
                    line_chart_btc_abc.history_key("abc"),
                    "-inf",
                    now - line_chart_btc_abc.RETENTION_SECONDS - 1,
                ),
            ],
        )

    def test_reset_and_seed_history_deletes_only_own_series_keys(self):
        redis_client = Mock()

        def make_sample(timestamp):
            return {
                "timestamp": timestamp,
                "btc": float(timestamp),
                "abc": float(timestamp) - 1,
            }

        with patch.object(line_chart_btc_abc, "create_sample", side_effect=make_sample):
            seeded_count = line_chart_btc_abc.reset_and_seed_history(
                redis_client,
                now=100,
                history_seconds=10,
                interval_seconds=5,
            )

        self.assertEqual(seeded_count, 3)
        redis_client.delete.assert_called_once_with(
            line_chart_btc_abc.history_key("btc"),
            line_chart_btc_abc.history_key("abc"),
        )
        self.assertEqual(len(redis_client.zadd.call_args_list), len(line_chart_btc_abc.SERIES_NAMES))

        stored_members_by_key = {
            zadd_call.args[0]: zadd_call.args[1]
            for zadd_call in redis_client.zadd.call_args_list
        }
        expected_points = {
            line_chart_btc_abc.history_key("btc"): [
                {"timestamp": 90, "value": 90.0},
                {"timestamp": 95, "value": 95.0},
                {"timestamp": 100, "value": 100.0},
            ],
            line_chart_btc_abc.history_key("abc"): [
                {"timestamp": 90, "value": 89.0},
                {"timestamp": 95, "value": 94.0},
                {"timestamp": 100, "value": 99.0},
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

        with patch.object(line_chart_btc_abc, "run_once") as run_once:
            with self.assertRaises(StopLoop):
                line_chart_btc_abc.run_forever(
                    redis_client,
                    sleep=stop,
                    time_func=lambda: 123,
                )

        run_once.assert_called_once_with(redis_client, now=123)

    def test_run_forever_can_sleep_before_first_iteration(self):
        redis_client = Mock()
        sleep = Mock(side_effect=[None, StopLoop()])

        with patch.object(line_chart_btc_abc, "run_once") as run_once:
            with self.assertRaises(StopLoop):
                line_chart_btc_abc.run_forever(
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
