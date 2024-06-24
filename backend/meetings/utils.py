import calendar
import logging
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)


def get_next_occurrence_date(recurrence, source_datetime):
    if recurrence.frequency == "daily":
        return source_datetime + timedelta(days=recurrence.interval)
    elif recurrence.frequency == "weekly":
        return source_datetime + timedelta(weeks=recurrence.interval)
    elif recurrence.frequency == "monthly":
        next_date = source_datetime + relativedelta(months=recurrence.interval)
        if recurrence.week_day is not None:
            days_in_month = calendar.monthrange(next_date.year, next_date.month)[1]
            week_day_occurrences = [
                day
                for day in range(1, days_in_month + 1)
                if date(next_date.year, next_date.month, day).weekday()
                == recurrence.week_day
            ]
            if recurrence.month_week <= len(week_day_occurrences):
                day = week_day_occurrences[recurrence.month_week - 1]
            else:
                day = week_day_occurrences[-1]
            next_date = next_date.replace(day=day)
        return next_date
    else:
        # Custom recurrence logic to be added later
        return None
