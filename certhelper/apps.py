from django.apps import AppConfig


class CerthelperConfig(AppConfig):
    name = 'certhelper'

    def ready(self):
        # noinspection PyUnresolvedReferences
        import certhelper.signals
