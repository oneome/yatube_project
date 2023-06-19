from datetime import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    current_year = datetime.utcnow().year
    return {
        'year': current_year
    }
