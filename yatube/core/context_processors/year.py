from django.utils import timezone


def year(*_):
    """Добавляет переменную с текущим годом."""
    return {'year': timezone.now().strftime('%Y')}
