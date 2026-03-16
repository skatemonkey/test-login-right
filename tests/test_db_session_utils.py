from types import SimpleNamespace
import unittest
from unittest.mock import sentinel

from app.shared.utils import db_session_utils


class DbSessionUtilsTestCase(unittest.TestCase):
    def test_commit_session_commits(self):
        original_commit = db_session_utils.db.session.commit
        original_rollback = db_session_utils.db.session.rollback

        events: list[str] = []

        def fake_commit():
            events.append("commit")

        def fake_rollback():
            events.append("rollback")

        db_session_utils.db.session.commit = fake_commit
        db_session_utils.db.session.rollback = fake_rollback
        try:
            db_session_utils.commit_session()
        finally:
            db_session_utils.db.session.commit = original_commit
            db_session_utils.db.session.rollback = original_rollback

        self.assertEqual(events, ["commit"])

    def test_commit_session_rolls_back_on_failure(self):
        original_commit = db_session_utils.db.session.commit
        original_rollback = db_session_utils.db.session.rollback

        events: list[str] = []

        def fake_commit():
            events.append("commit")
            raise RuntimeError("boom")

        def fake_rollback():
            events.append("rollback")

        db_session_utils.db.session.commit = fake_commit
        db_session_utils.db.session.rollback = fake_rollback
        try:
            with self.assertRaises(RuntimeError):
                db_session_utils.commit_session()
        finally:
            db_session_utils.db.session.commit = original_commit
            db_session_utils.db.session.rollback = original_rollback

        self.assertEqual(events, ["commit", "rollback"])

    def test_commit_and_refresh_refreshes_instance(self):
        original_commit = db_session_utils.db.session.commit
        original_rollback = db_session_utils.db.session.rollback
        original_refresh = db_session_utils.db.session.refresh

        events: list[tuple[str, object]] = []

        def fake_commit():
            events.append(("commit", None))

        def fake_rollback():
            events.append(("rollback", None))

        def fake_refresh(instance):
            events.append(("refresh", instance))

        item = SimpleNamespace(id=1)

        db_session_utils.db.session.commit = fake_commit
        db_session_utils.db.session.rollback = fake_rollback
        db_session_utils.db.session.refresh = fake_refresh
        try:
            result = db_session_utils.commit_and_refresh(item)
        finally:
            db_session_utils.db.session.commit = original_commit
            db_session_utils.db.session.rollback = original_rollback
            db_session_utils.db.session.refresh = original_refresh

        self.assertIs(result, item)
        self.assertEqual(events, [("commit", None), ("refresh", item)])

    def test_commit_and_refresh_rolls_back_before_reraising(self):
        original_commit = db_session_utils.db.session.commit
        original_rollback = db_session_utils.db.session.rollback
        original_refresh = db_session_utils.db.session.refresh

        events: list[str] = []

        def fake_commit():
            events.append("commit")
            raise RuntimeError("boom")

        def fake_rollback():
            events.append("rollback")

        def fake_refresh(_instance):
            events.append("refresh")

        db_session_utils.db.session.commit = fake_commit
        db_session_utils.db.session.rollback = fake_rollback
        db_session_utils.db.session.refresh = fake_refresh
        try:
            with self.assertRaises(RuntimeError):
                db_session_utils.commit_and_refresh(sentinel.instance)
        finally:
            db_session_utils.db.session.commit = original_commit
            db_session_utils.db.session.rollback = original_rollback
            db_session_utils.db.session.refresh = original_refresh

        self.assertEqual(events, ["commit", "rollback"])


if __name__ == "__main__":
    unittest.main()
