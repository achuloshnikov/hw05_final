from django.utils import timezone


def year(request):
    """Добавляет переменную с текущим годом."""
    return {'year': timezone.now().strftime('%Y')}


def date(request):
    """Добавляет переменную с текущим годом."""
    return {'date': timezone.now()}
