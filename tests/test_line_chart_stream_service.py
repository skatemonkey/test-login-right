from queue import Empty
import unittest

from app.module.line_chart.line_chart_stream_service import LineChartStreamHub


class LineChartStreamServiceTestCase(unittest.TestCase):
    def test_subscribe_unsubscribe_updates_connection_count(self):
        hub = LineChartStreamHub(queue_size=5)

        connection_id, _ = hub.subscribe(["cpu"])
        self.assertEqual(hub.subscriber_count(), 1)

        hub.unsubscribe(connection_id)
        self.assertEqual(hub.subscriber_count(), 0)

    def test_publish_fans_out_and_applies_series_filter(self):
        hub = LineChartStreamHub(queue_size=5)
        _, cpu_queue = hub.subscribe(["cpu"])
        _, memory_queue = hub.subscribe(["memory"])

        hub.publish({"timestamp": 1710000000, "cpu": 11, "memory": 22, "network": 33})

        self.assertEqual(
            cpu_queue.get_nowait(),
            {"timestamp": 1710000000, "values": {"cpu": 11.0}},
        )
        self.assertEqual(
            memory_queue.get_nowait(),
            {"timestamp": 1710000000, "values": {"memory": 22.0}},
        )

        with self.assertRaises(Empty):
            cpu_queue.get_nowait()

    def test_publish_sends_to_multiple_subscribers_for_same_series(self):
        hub = LineChartStreamHub(queue_size=5)
        _, queue_1 = hub.subscribe(["cpu"])
        _, queue_2 = hub.subscribe(["cpu"])

        hub.publish({"timestamp": 1710000010, "cpu": 15})

        expected_payload = {"timestamp": 1710000010, "values": {"cpu": 15.0}}
        self.assertEqual(queue_1.get_nowait(), expected_payload)
        self.assertEqual(queue_2.get_nowait(), expected_payload)

    def test_handle_pubsub_message_ignores_malformed_payload(self):
        hub = LineChartStreamHub(queue_size=5)
        _, queue = hub.subscribe(["cpu"])

        hub.handle_pubsub_message("not-json")
        hub.handle_pubsub_message('{"timestamp": "x", "cpu": 1}')

        with self.assertRaises(Empty):
            queue.get_nowait()


if __name__ == "__main__":
    unittest.main()
