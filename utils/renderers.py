from rest_framework.renderers import BrowsableAPIRenderer


class CustomBrowsableAPIRenderer(BrowsableAPIRenderer):
    template = "drf/custom_drf_api.html"

    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)
        context["name"] = "API"
        context["version"] = "v1.0"
        return context
