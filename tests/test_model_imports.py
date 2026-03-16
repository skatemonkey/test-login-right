import importlib
import unittest


class ModelImportTests(unittest.TestCase):
    def test_model_modules_import_from_shared_model_package(self):
        module_names = [
            "app.shared.model.audit_log",
            "app.shared.model.notification",
            "app.shared.model.permission",
            "app.shared.model.user",
            "app.shared.model.user_permission",
        ]

        for module_name in module_names:
            with self.subTest(module_name=module_name):
                module = importlib.import_module(module_name)
                self.assertIsNotNone(module)

    def test_services_import_with_model_package_dependencies(self):
        module_names = [
            "app.module.audit.audit_service",
            "app.module.auth.auth_service",
            "app.module.notification.notification_service",
            "app.module.permission.permission_service",
            "app.module.user.user_service",
        ]

        for module_name in module_names:
            with self.subTest(module_name=module_name):
                module = importlib.import_module(module_name)
                self.assertIsNotNone(module)
