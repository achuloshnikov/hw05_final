from django.utils import timezone


def year(*_) -> dict:
    """Добавляет переменную с текущим годом.

    Returns:
        Возвращает текущий год.
    """
    return {'year': timezone.now().strftime('%Y')}
