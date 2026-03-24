import unittest
from unittest.mock import Mock, call, patch

from app.module.line_chart import line_chart_redis_repository


class LineChartRedisRepositoryTestCase(unittest.TestCase):
    def test_fetch_history_rows_queries_each_series_key(self):
        redis_client = Mock()
        pipeline = Mock()
        pipeline.execute.return_value = [["cpu-row"], ["memory-row-1", "memory-row-2"]]
        redis_client.pipeline.return_value = pipeline

        with patch.object(
            line_chart_redis_repository.redis_ext,
            "get_redis",
            return_value=redis_client,
        ):
            rows = line_chart_redis_repository.fetch_history_rows(["cpu", "memory"], 10, 20)

        self.assertEqual(
            rows,
            {
                "cpu": ["cpu-row"],
                "memory": ["memory-row-1", "memory-row-2"],
            },
        )
        redis_client.pipeline.assert_called_once_with()
        self.assertEqual(
            pipeline.zrangebyscore.call_args_list,
            [
                call(line_chart_redis_repository.history_key("cpu"), 10, 20),
                call(line_chart_redis_repository.history_key("memory"), 10, 20),
            ],
        )
        pipeline.execute.assert_called_once_with()

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
