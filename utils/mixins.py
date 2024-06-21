from rest_framework.settings import api_settings


class CustomCreateModelMixin:
    """
    Custom Create a model instance.
    """

    def perform_create(self, serializer):
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {"Location": str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}
