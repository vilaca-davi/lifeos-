from dateutil.rrule import rrulestr
from datetime import timedelta


def get_occurrences(event, range_start, range_end):
    """
    Retorna as datas em que um evento (recorrente ou não) ocorre
    dentro do intervalo [range_start, range_end].
    """
    if not event.is_recurring or not event.recurrence_rule:
        if range_start <= event.start_datetime <= range_end:
            return [event.start_datetime]
        return []

    duration = timedelta()
    if event.end_datetime:
        duration = event.end_datetime - event.start_datetime

    try:
        rule = rrulestr(event.recurrence_rule, dtstart=event.start_datetime)
        occurrences = rule.between(range_start, range_end, inc=True)
        return occurrences
    except Exception:
        return []