import unittest

from app.shared.schemas.api_response_schema import ErrorResponse


class ErrorResponseSchemaTestCase(unittest.TestCase):
    def test_model_dump_omits_details_when_unset(self):
        payload = ErrorResponse(error="Something went wrong")

        self.assertEqual(payload.model_dump(), {"error": "Something went wrong"})

    def test_model_dump_includes_string_details(self):
        payload = ErrorResponse(
            error="Something went wrong",
            details="Try again later",
        )

        self.assertEqual(
            payload.model_dump(),
            {
                "error": "Something went wrong",
                "details": "Try again later",
            },
        )

    def test_model_dump_includes_object_details(self):
        payload = ErrorResponse(
            error="Something went wrong",
            details={"field": "username"},
        )

        self.assertEqual(
            payload.model_dump(),
            {
                "error": "Something went wrong",
                "details": {"field": "username"},
            },
        )


if __name__ == "__main__":
    unittest.main()
