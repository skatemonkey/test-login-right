from datetime import datetime
import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from sqlalchemy.exc import IntegrityError

from app.module.audit import audit_service
from app.module.auth import auth_service
from app.module.notification import notification_service
from app.module.permission import permission_service
from app.module.user import user_service
from app.shared.schemas.audit_schema import AuditLogQuery, AuditLogRequest
from app.shared.schemas.auth_schema import LoginRequest
from app.shared.schemas.permission_schema import (
    PermissionCreateRequest,
    PermissionListQuery,
    PermissionUpdateRequest,
)
from app.shared.schemas.user_schema import UserCreateRequest, UserListQuery, UserUpdateRequest


class AuthServiceTestCase(unittest.TestCase):
    def test_login_returns_token_and_permissions_from_repository(self):
        user = SimpleNamespace(
            user_id=7,
            username="alice",
            password_hash="stored-hash",
            permissions=[
                SimpleNamespace(permission=SimpleNamespace(module="user", action="view")),
                SimpleNamespace(permission=SimpleNamespace(module="user", action="update")),
            ],
        )

        with patch.object(auth_service.auth_repository, "get_user_by_username", return_value=user) as get_user:
            with patch.object(auth_service, "_verify_password", return_value=True) as verify_password:
                with patch.object(auth_service, "create_access_token", return_value="jwt-token") as create_token:
                    result, status = auth_service.login(
                        LoginRequest(username="alice", password="secret"),
                    )

        self.assertEqual(status, 200)
        self.assertEqual(
            result.model_dump(),
            {
                "userId": 7,
                "username": "alice",
                "accessToken": "jwt-token",
                "permissions": ["user.view", "user.update"],
            },
        )
        get_user.assert_called_once_with("alice")
        verify_password.assert_called_once_with("secret", "stored-hash")
        create_token.assert_called_once_with(
            identity="7",
            additional_claims={"username": "alice"},
        )


class AuditServiceTestCase(unittest.TestCase):
    def test_create_log_serializes_dict_details_before_repository_call(self):
        request = AuditLogRequest(
            userId=1,
            module="audit",
            action="create",
            device="browser",
            details={"source": "ui"},
        )

        with patch.object(audit_service.audit_repository, "create_log") as create_log:
            result, status = audit_service.create_log(request, ip="127.0.0.1")

        self.assertEqual(status, 201)
        self.assertEqual(result, {"message": "logged"})
        create_log.assert_called_once_with(
            user_id=1,
            ip="127.0.0.1",
            module="audit",
            action="create",
            device="browser",
            details=json.dumps({"source": "ui"}),
        )

    def test_get_logs_maps_repository_rows_to_paginated_response(self):
        log = SimpleNamespace(
            id=3,
            ip="127.0.0.1",
            device="browser",
            created_at=datetime(2024, 1, 2, 3, 4, 5),
            module="auth",
            action="login",
            details="ok",
        )
        query = AuditLogQuery(page=2, pageSize=5)

        with patch.object(audit_service.audit_repository, "query_logs", return_value=([(log, "alice")], 1, 1)):
            result, status = audit_service.get_logs(query)

        self.assertEqual(status, 200)
        self.assertEqual(
            result.model_dump(),
            {
                "data": [
                    {
                        "id": 3,
                        "username": "alice",
                        "ip": "127.0.0.1",
                        "device": "browser",
                        "createdAt": "2024-01-02 03:04:05",
                        "module": "auth",
                        "action": "login",
                        "details": "ok",
                    },
                ],
                "page": 2,
                "pageSize": 5,
                "totalElements": 1,
                "totalPages": 1,
            },
        )


class NotificationServiceTestCase(unittest.TestCase):
    def test_create_notification_publishes_repository_payload(self):
        notification = SimpleNamespace(
            id=9,
            user_id=5,
            message="approved",
            is_read=False,
            created_at=datetime(2024, 2, 3, 4, 5, 6),
        )

        with patch.object(
            notification_service.notification_repository,
            "create_notification",
            return_value=notification,
        ) as create_notification:
            with patch.object(notification_service.notification_stream.notification_hub, "publish") as publish:
                result, status = notification_service.create_notification(5, "approved")

        self.assertEqual(status, 201)
        self.assertEqual(
            result,
            {
                "message": "Notification sent",
                "notification": {
                    "id": 9,
                    "userId": 5,
                    "message": "approved",
                    "isRead": False,
                    "createdAt": "2024-02-03 04:05:06",
                },
            },
        )
        create_notification.assert_called_once_with(5, "approved")
        publish.assert_called_once_with(
            5,
            {
                "type": "notification.created",
                "notification": {
                    "id": 9,
                    "userId": 5,
                    "message": "approved",
                    "isRead": False,
                    "createdAt": "2024-02-03 04:05:06",
                },
            },
        )

    def test_list_notifications_paginated_maps_repository_result(self):
        notification = SimpleNamespace(
            id=1,
            user_id=2,
            message="hello",
            is_read=True,
            created_at=datetime(2024, 3, 4, 5, 6, 7),
        )

        with patch.object(
            notification_service.notification_repository,
            "list_notifications_paginated",
            return_value=([notification], 3, 2),
        ):
            result, status = notification_service.list_notifications_paginated(2, 1, 2)

        self.assertEqual(status, 200)
        self.assertEqual(
            result.model_dump(),
            {
                "data": [
                    {
                        "id": 1,
                        "userId": 2,
                        "message": "hello",
                        "isRead": True,
                        "createdAt": "2024-03-04 05:06:07",
                    },
                ],
                "page": 1,
                "pageSize": 2,
                "totalElements": 3,
                "totalPages": 2,
                "hasMore": True,
            },
        )


class PermissionServiceTestCase(unittest.TestCase):
    def test_get_permissions_maps_repository_rows(self):
        permission = SimpleNamespace(
            permission_id=4,
            module="user",
            action="view",
            description="Can view users",
            is_active=True,
            created_at=datetime(2024, 4, 5, 6, 7, 8),
            updated_at=datetime(2024, 4, 5, 6, 7, 9),
        )
        query = PermissionListQuery(page=1, pageSize=10)

        with patch.object(
            permission_service.permission_repository,
            "get_permissions",
            return_value=([permission], 1, 1),
        ):
            result, status = permission_service.get_permissions(query)

        self.assertEqual(status, 200)
        self.assertEqual(
            result.model_dump(),
            {
                "data": [
                    {
                        "permissionId": 4,
                        "module": "user",
                        "action": "view",
                        "description": "Can view users",
                        "isActive": True,
                        "createdAt": "2024-04-05 06:07:08",
                        "updatedAt": "2024-04-05 06:07:09",
                    },
                ],
                "page": 1,
                "pageSize": 10,
                "totalElements": 1,
                "totalPages": 1,
            },
        )

    def test_create_permission_returns_conflict_when_duplicate_exists(self):
        body = PermissionCreateRequest(module="user", action="view", description=None, isActive=True)

        with patch.object(
            permission_service.permission_repository,
            "get_permission_by_module_and_action",
            return_value=object(),
        ):
            result, status = permission_service.create_permission(body)

        self.assertEqual(status, 409)
        self.assertEqual(result.model_dump(), {"error": "Permission already exists"})

    def test_create_permission_returns_msg_data_response(self):
        body = PermissionCreateRequest(module="user", action="view", description="Can view", isActive=True)
        permission = SimpleNamespace(
            permission_id=4,
            module="user",
            action="view",
            description="Can view",
            is_active=True,
            created_at=datetime(2024, 4, 5, 6, 7, 8),
            updated_at=datetime(2024, 4, 5, 6, 7, 9),
        )

        with patch.object(
            permission_service.permission_repository,
            "get_permission_by_module_and_action",
            return_value=None,
        ):
            with patch.object(
                permission_service.permission_repository,
                "create_permission",
                return_value=permission,
            ):
                result, status = permission_service.create_permission(body)

        self.assertEqual(status, 201)
        self.assertEqual(
            result.model_dump(),
            {
                "msgCode": "permission.created",
                "data": {
                    "permissionId": 4,
                    "module": "user",
                    "action": "view",
                    "description": "Can view",
                    "isActive": True,
                    "createdAt": "2024-04-05 06:07:08",
                    "updatedAt": "2024-04-05 06:07:09",
                },
            },
        )

    def test_update_permission_returns_conflict_on_integrity_error(self):
        body = PermissionUpdateRequest(module="user", action="edit", description=None, isActive=True)
        permission = SimpleNamespace()

        with patch.object(
            permission_service.permission_repository,
            "get_permission_by_id",
            return_value=permission,
        ):
            with patch.object(
                permission_service.permission_repository,
                "get_permission_by_module_and_action",
                return_value=None,
            ):
                with patch.object(
                    permission_service.permission_repository,
                    "update_permission",
                    side_effect=IntegrityError("stmt", "params", Exception("duplicate")),
                ):
                    result, status = permission_service.update_permission(4, body)

        self.assertEqual(status, 409)
        self.assertEqual(result.model_dump(), {"error": "Permission already exists"})

    def test_update_permission_returns_msg_data_response(self):
        body = PermissionUpdateRequest(module="user", action="edit", description="Can edit", isActive=True)
        existing_permission = SimpleNamespace()
        updated_permission = SimpleNamespace(
            permission_id=4,
            module="user",
            action="edit",
            description="Can edit",
            is_active=True,
            created_at=datetime(2024, 4, 5, 6, 7, 8),
            updated_at=datetime(2024, 4, 5, 6, 7, 10),
        )

        with patch.object(
            permission_service.permission_repository,
            "get_permission_by_id",
            return_value=existing_permission,
        ):
            with patch.object(
                permission_service.permission_repository,
                "get_permission_by_module_and_action",
                return_value=None,
            ):
                with patch.object(
                    permission_service.permission_repository,
                    "update_permission",
                    return_value=updated_permission,
                ):
                    result, status = permission_service.update_permission(4, body)

        self.assertEqual(status, 200)
        self.assertEqual(
            result.model_dump(),
            {
                "msgCode": "permission.updated",
                "data": {
                    "permissionId": 4,
                    "module": "user",
                    "action": "edit",
                    "description": "Can edit",
                    "isActive": True,
                    "createdAt": "2024-04-05 06:07:08",
                    "updatedAt": "2024-04-05 06:07:10",
                },
            },
        )


class UserServiceTestCase(unittest.TestCase):
    def test_query_users_maps_repository_rows_and_permission_counts(self):
        user = SimpleNamespace(
            user_id=8,
            username="alice",
            email="alice@example.com",
            is_active=True,
            created_at=datetime(2024, 5, 6, 7, 8, 9),
            updated_at=datetime(2024, 5, 6, 7, 8, 10),
        )
        query = UserListQuery(page=1, pageSize=10)

        with patch.object(user_service.user_repository, "query_users", return_value=([user], 1, 1)):
            with patch.object(
                user_service.user_repository,
                "get_permission_count_map",
                return_value={8: 3},
            ):
                result, status = user_service.query_users(query)

        self.assertEqual(status, 200)
        self.assertEqual(
            result.model_dump(),
            {
                "data": [
                    {
                        "userId": 8,
                        "username": "alice",
                        "email": "alice@example.com",
                        "isActive": True,
                        "permissionCount": 3,
                        "createdAt": "2024-05-06 07:08:09",
                        "updatedAt": "2024-05-06 07:08:10",
                    },
                ],
                "page": 1,
                "pageSize": 10,
                "totalElements": 1,
                "totalPages": 1,
            },
        )

    def test_get_user_detail_maps_permission_ids(self):
        user = SimpleNamespace(
            user_id=8,
            username="alice",
            email="alice@example.com",
            is_active=True,
            created_at=datetime(2024, 5, 6, 7, 8, 9),
            updated_at=datetime(2024, 5, 6, 7, 8, 10),
            permissions=[
                SimpleNamespace(permission_id=3),
                SimpleNamespace(permission_id=1),
            ],
        )

        with patch.object(user_service.user_repository, "get_user_by_id", return_value=user):
            result, status = user_service.get_user_detail(8)

        self.assertEqual(status, 200)
        self.assertEqual(
            result.model_dump(),
            {
                "userId": 8,
                "username": "alice",
                "email": "alice@example.com",
                "isActive": True,
                "permissionIds": [1, 3],
                "createdAt": "2024-05-06 07:08:09",
                "updatedAt": "2024-05-06 07:08:10",
            },
        )

    def test_get_permission_matrix_returns_direct_array_sorted(self):
        permissions = [
            SimpleNamespace(permission_id=8, module="user", action="delete"),
            SimpleNamespace(permission_id=6, module="audit", action="approve"),
            SimpleNamespace(permission_id=7, module="user", action="view"),
            SimpleNamespace(permission_id=5, module="user", action="create"),
        ]

        with patch.object(
            user_service.user_repository,
            "get_active_permissions",
            return_value=permissions,
        ):
            result, status = user_service.get_permission_matrix()

        self.assertEqual(status, 200)
        self.assertEqual(
            result.model_dump(),
            [
                {"permissionId": 6, "module": "audit", "action": "approve"},
                {"permissionId": 7, "module": "user", "action": "view"},
                {"permissionId": 5, "module": "user", "action": "create"},
                {"permissionId": 8, "module": "user", "action": "delete"},
            ],
        )

    def test_create_user_returns_conflict_when_username_exists(self):
        body = UserCreateRequest(
            username="alice",
            email="alice@example.com",
            password="password123",
            isActive=True,
        )

        with patch.object(user_service.user_repository, "username_exists", return_value=True):
            result, status = user_service.create_user(body)

        self.assertEqual(status, 409)
        self.assertEqual(result.model_dump(), {"error": "Username already exists"})

    def test_create_user_returns_msg_data_response(self):
        body = UserCreateRequest(
            username="alice",
            email="alice@example.com",
            password="password123",
            isActive=True,
        )
        user = SimpleNamespace(
            user_id=8,
            username="alice",
            email="alice@example.com",
            is_active=True,
            created_at=datetime(2024, 5, 6, 7, 8, 9),
            updated_at=datetime(2024, 5, 6, 7, 8, 10),
            permissions=[],
        )

        with patch.object(user_service.user_repository, "username_exists", return_value=False):
            with patch.object(user_service, "_hash_password", return_value="hashed-password"):
                with patch.object(user_service.user_repository, "create_user", return_value=user):
                    result, status = user_service.create_user(body)

        self.assertEqual(status, 201)
        self.assertEqual(
            result.model_dump(),
            {
                "msgCode": "user.created",
                "data": {
                    "userId": 8,
                    "username": "alice",
                    "email": "alice@example.com",
                    "isActive": True,
                    "permissionIds": [],
                    "createdAt": "2024-05-06 07:08:09",
                    "updatedAt": "2024-05-06 07:08:10",
                },
            },
        )

    def test_update_user_returns_msg_data_response(self):
        body = UserUpdateRequest(
            username="alice",
            email="alice@example.com",
            password="password123",
            isActive=True,
        )
        existing_user = SimpleNamespace()
        updated_user = SimpleNamespace(
            user_id=8,
            username="alice",
            email="alice@example.com",
            is_active=True,
            created_at=datetime(2024, 5, 6, 7, 8, 9),
            updated_at=datetime(2024, 5, 6, 7, 8, 10),
            permissions=[],
        )

        with patch.object(user_service.user_repository, "get_user_by_id", return_value=existing_user):
            with patch.object(user_service.user_repository, "username_exists", return_value=False):
                with patch.object(user_service, "_hash_password", return_value="hashed-password"):
                    with patch.object(
                        user_service.user_repository,
                        "update_user",
                        return_value=updated_user,
                    ):
                        result, status = user_service.update_user(8, body)

        self.assertEqual(status, 200)
        self.assertEqual(
            result.model_dump(),
            {
                "msgCode": "user.updated",
                "data": {
                    "userId": 8,
                    "username": "alice",
                    "email": "alice@example.com",
                    "isActive": True,
                    "permissionIds": [],
                    "createdAt": "2024-05-06 07:08:09",
                    "updatedAt": "2024-05-06 07:08:10",
                },
            },
        )

    def test_toggle_user_permission_returns_msg_data_response(self):
        user = SimpleNamespace()
        permission = SimpleNamespace(action="view", is_active=True)

        with patch.object(user_service.user_repository, "get_user_by_id", return_value=user):
            with patch.object(user_service.user_repository, "get_permission_by_id", return_value=permission):
                with patch.object(user_service.user_repository, "set_user_permission") as set_user_permission:
                    result, status = user_service.toggle_user_permission(8, 4, True)

        self.assertEqual(status, 200)
        self.assertEqual(
            result.model_dump(),
            {
                "msgCode": "user.permission.updated",
                "data": {
                    "userId": 8,
                    "permissionId": 4,
                    "enabled": True,
                },
            },
        )
        set_user_permission.assert_called_once_with(8, 4, True)


if __name__ == "__main__":
    unittest.main()
