from utils.dates import (
    get_today, get_now, parse_date, parse_datetime,
    format_date, calculate_age, is_expired, days_until
)
from datetime import date, datetime


def test_get_today():
    today = get_today()
    assert len(today) == 10
    assert today.count("-") == 2
    assert isinstance(today, str)


def test_get_now():
    now = get_now()
    assert len(now) >= 19
    assert isinstance(now, str)


def test_parse_date_valid():
    d = parse_date("2026-01-15")
    assert d is not None
    assert d.year == 2026
    assert d.month == 1
    assert d.day == 15


def test_parse_date_invalid():
    assert parse_date("invalid") is None
    assert parse_date("2026-13-01") is None
    assert parse_date("") is None


def test_parse_datetime_valid():
    dt = parse_datetime("2026-01-15 10:30:00")
    assert dt is not None
    assert dt.year == 2026
    assert dt.hour == 10


def test_parse_datetime_invalid():
    assert parse_datetime("invalid") is None
    assert parse_datetime("") is None


def test_format_date():
    d = date(2026, 1, 15)
    assert format_date(d) == "2026-01-15"


def test_format_datetime():
    dt = datetime(2026, 1, 15, 10, 30, 0)
    result = format_date(dt)
    assert "2026-01-15" in result


def test_calculate_age():
    birth = "2000-01-01"
    age = calculate_age(birth)
    assert age >= 25
    assert age <= 27


def test_calculate_age_invalid():
    assert calculate_age("invalid") == 0


def test_is_expired():
    assert is_expired("2020-01-01") is True
    assert is_expired("2099-12-31") is False


def test_is_expired_invalid():
    assert is_expired("invalid") is False


def test_days_until():
    result = days_until("2099-12-31")
    assert result > 0


def test_days_until_past():
    result = days_until("2020-01-01")
    assert result < 0


def test_days_until_invalid():
    assert days_until("invalid") == 0
