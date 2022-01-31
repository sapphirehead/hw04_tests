from django.utils import timezone


def year(request):
    """Добавляет в контекст переменную year с текущим годом."""
    return {
        'year': timezone.now().year,
    }
