from django.apps import AppConfig


class DjangoXRayConfig(AppConfig):
    name = 'django_aws_xray'
    verbose_name = "Django AWS X-Ray"

    def ready(self):
        from . import patches  # noqa
