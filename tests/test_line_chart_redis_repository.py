import unittest
from unittest.mock import Mock, call, patch

from app.module.line_chart import line_chart_redis_repository


class LineChartRedisRepositoryTestCase(unittest.TestCase):
    def test_fetch_history_series_returns_requested_series_in_order(self):
        redis_client = Mock()
        pipeline = Mock()
        ts_client = pipeline.ts.return_value
        pipeline.execute.return_value = [
            [(10, 20), (11, 21)],
            [(10, 45), (11, 46)],
        ]
        redis_client.pipeline.return_value = pipeline

        with patch.object(
            line_chart_redis_repository.redis_ext,
            "get_redis",
            return_value=redis_client,
        ):
            series = line_chart_redis_repository.fetch_history_series(["cpu", "memory"], 10, 20)

        self.assertEqual(
            [item.model_dump() for item in series],
            [
                {
                    "name": "cpu",
                    "data": [
                        {"x": 10, "y": 20.0},
                        {"x": 11, "y": 21.0},
                    ],
                },
                {
                    "name": "memory",
                    "data": [
                        {"x": 10, "y": 45.0},
                        {"x": 11, "y": 46.0},
                    ],
                },
            ],
        )
        redis_client.pipeline.assert_called_once_with()
        pipeline.ts.assert_called_once_with()
        self.assertEqual(
            ts_client.range.call_args_list,
            [
                call(line_chart_redis_repository.history_key("cpu"), 10, 20),
                call(line_chart_redis_repository.history_key("memory"), 10, 20),
            ],
        )
        pipeline.execute.assert_called_once_with()

    def test_fetch_history_series_preserves_duplicate_and_case_sensitive_requests(self):
        redis_client = Mock()
        pipeline = Mock()
        ts_client = pipeline.ts.return_value
        pipeline.execute.return_value = [
            [],
            [(10, 20)],
            [(10, 20)],
        ]
        redis_client.pipeline.return_value = pipeline

        with patch.object(
            line_chart_redis_repository.redis_ext,
            "get_redis",
            return_value=redis_client,
        ):
            series = line_chart_redis_repository.fetch_history_series(["CPU", "cpu", "cpu"], 10, 20)

        self.assertEqual(
            [item.model_dump() for item in series],
            [
                {"name": "CPU", "data": []},
                {"name": "cpu", "data": [{"x": 10, "y": 20.0}]},
                {"name": "cpu", "data": [{"x": 10, "y": 20.0}]},
            ],
        )
        self.assertEqual(
            ts_client.range.call_args_list,
            [
                call(line_chart_redis_repository.history_key("CPU"), 10, 20),
                call(line_chart_redis_repository.history_key("cpu"), 10, 20),
                call(line_chart_redis_repository.history_key("cpu"), 10, 20),
            ],
        )

    def test_fetch_history_series_ignores_malformed_rows(self):
        redis_client = Mock()
        pipeline = Mock()
        pipeline.ts.return_value = Mock()
        pipeline.execute.return_value = [[
            "not-a-point",
            ("bad", 1),
            (10, "n/a"),
            (11, 18.5),
        ]]
        redis_client.pipeline.return_value = pipeline

        with patch.object(
            line_chart_redis_repository.redis_ext,
            "get_redis",
            return_value=redis_client,
        ):
            series = line_chart_redis_repository.fetch_history_series(["cpu"], 10, 20)

        self.assertEqual(
            [item.model_dump() for item in series],
            [
                {
                    "name": "cpu",
                    "data": [{"x": 11, "y": 18.5}],
                },
            ],
        )

    def test_fetch_history_series_returns_empty_points_for_empty_window(self):
        redis_client = Mock()
        pipeline = Mock()
        pipeline.ts.return_value = Mock()
        pipeline.execute.return_value = [[], []]
        redis_client.pipeline.return_value = pipeline

        with patch.object(
            line_chart_redis_repository.redis_ext,
            "get_redis",
            return_value=redis_client,
        ):
            series = line_chart_redis_repository.fetch_history_series(["cpu", "network"], 10, 20)

        self.assertEqual(
            [item.model_dump() for item in series],
            [
                {"name": "cpu", "data": []},
                {"name": "network", "data": []},
            ],
        )

    def test_listen_for_live_updates_forwards_messages_and_cleans_up(self):
        redis_client = Mock()
        pubsub = Mock()
        redis_client.pubsub.return_value = pubsub
        pubsub.listen.return_value = iter(
            [
                {"type": "subscribe", "data": 1},
                {"type": "message", "data": '{"timestamp":1,"cpu":2}'},
                {"type": "message", "data": 123},
            ],
        )
        handle_message = Mock()
        stop_states = iter([False, False, False, True])

        with patch.object(
            line_chart_redis_repository.redis.Redis,
            "from_url",
            return_value=redis_client,
        ) as from_url:
            line_chart_redis_repository.listen_for_live_updates(
                redis_url="redis://example",
                handle_message=handle_message,
                should_stop=lambda: next(stop_states),
            )

        from_url.assert_called_once_with("redis://example", decode_responses=True)
        redis_client.pubsub.assert_called_once_with(ignore_subscribe_messages=True)
        pubsub.subscribe.assert_called_once_with(line_chart_redis_repository.LIVE_UPDATES_CHANNEL)
        handle_message.assert_called_once_with('{"timestamp":1,"cpu":2}')
        pubsub.close.assert_called_once_with()
        redis_client.close.assert_called_once_with()

    def test_listen_for_live_updates_retries_after_error(self):
        first_client = Mock()
        first_pubsub = Mock()
        first_client.pubsub.return_value = first_pubsub
        first_pubsub.listen.side_effect = RuntimeError("boom")

        second_client = Mock()
        second_pubsub = Mock()
        second_client.pubsub.return_value = second_pubsub
        second_pubsub.listen.return_value = iter([])

        handle_message = Mock()
        stop_states = iter([False, False, False, True])
        sleep = Mock()

        with patch.object(
            line_chart_redis_repository.redis.Redis,
            "from_url",
            side_effect=[first_client, second_client],
        ) as from_url:
            line_chart_redis_repository.listen_for_live_updates(
                redis_url="redis://example",
                handle_message=handle_message,
                should_stop=lambda: next(stop_states),
                sleep=sleep,
            )

        self.assertEqual(
            from_url.call_args_list,
            [
                call("redis://example", decode_responses=True),
                call("redis://example", decode_responses=True),
            ],
        )
        sleep.assert_called_once_with(line_chart_redis_repository.RECONNECT_DELAY_SECONDS)
        handle_message.assert_not_called()
        first_pubsub.close.assert_called_once_with()
        first_client.close.assert_called_once_with()
        second_pubsub.close.assert_called_once_with()
        second_client.close.assert_called_once_with()
