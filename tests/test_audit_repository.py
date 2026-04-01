import unittest
from unittest.mock import Mock

from app.module.audit import audit_repository
from app.shared.model.audit_log import AuditLog
from app.shared.schemas.audit_schema import AuditLogFilters


class AuditRepositoryTestCase(unittest.TestCase):
    def test_apply_audit_filters_includes_user_id_when_present(self):
        log_query = Mock()
        log_query.filter.return_value = log_query

        result = audit_repository._apply_audit_filters(
            log_query,
            AuditLogFilters(userId=9),
        )

        self.assertIs(result, log_query)
        first_filter = log_query.filter.call_args_list[0].args[0]
        self.assertEqual(str(first_filter), str(AuditLog.user_id == 9))

    def test_apply_audit_filters_matches_module_prefix_when_present(self):
        log_query = Mock()
        log_query.filter.return_value = log_query

        result = audit_repository._apply_audit_filters(
            log_query,
            AuditLogFilters(module="auth"),
        )

        self.assertIs(result, log_query)
        self.assertEqual(len(log_query.filter.call_args_list), 1)
        first_filter = log_query.filter.call_args_list[0].args[0]
        self.assertEqual(str(first_filter), str(AuditLog.module.like("auth%")))


if __name__ == "__main__":
    unittest.main()
