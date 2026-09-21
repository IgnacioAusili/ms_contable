from django.conf import settings


def app_info(request):
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "estudio": settings.ESTUDIO_CONTABLE,
        "developer": settings.DEVELOPER,
    }
