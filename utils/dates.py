from datetime import datetime, date


DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_now() -> str:
    return datetime.now().strftime(DATETIME_FORMAT)


def get_today() -> str:
    return date.today().strftime(DATE_FORMAT)


def parse_date(date_str: str) -> date | None:
    try:
        return datetime.strptime(date_str, DATE_FORMAT).date()
    except (ValueError, TypeError):
        return None


def parse_datetime(dt_str: str) -> datetime | None:
    try:
        return datetime.strptime(dt_str, DATETIME_FORMAT)
    except (ValueError, TypeError):
        return None


def format_date(d: date | datetime) -> str:
    if isinstance(d, datetime):
        return d.strftime(DATETIME_FORMAT)
    return d.strftime(DATE_FORMAT)


def calculate_age(birth_date: str | date) -> int:
    if isinstance(birth_date, str):
        birth_date = parse_date(birth_date)
    if birth_date is None:
        return 0
    today = date.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


def is_expired(due_date: str | date) -> bool:
    if isinstance(due_date, str):
        due_date = parse_date(due_date)
    if due_date is None:
        return False
    return date.today() > due_date


def days_until(due_date: str | date) -> int:
    if isinstance(due_date, str):
        due_date = parse_date(due_date)
    if due_date is None:
        return 0
    delta = due_date - date.today()
    return delta.days
