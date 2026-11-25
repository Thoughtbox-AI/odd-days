"""Odd days: the quirky and unofficial ones ("Hug A Bear Day"), dated for any year.

The list is odd_days.json: each day's name, what it's for (about), and the rule
that sets its date: a fixed date, the nth weekday of a month, days from an anchor
(Easter, US Thanksgiving, an equinox or solstice), a weekday on, before, after or
nearest another day, a weekday of a month's last full week or of the week holding
a date, the nearest working day, or the nth day of the year. A rule's `ref` is
itself a rule, so "the Monday after daylight saving starts" is a weekday after the
2nd Sunday of March. A day an organiser announces each year has the dates someone
looked up (`dates`, by year) and none after. The equinoxes and solstices need
`ephem` (pip install ephem); everything else is the standard library.

    python odd_days.py               # today's
    python odd_days.py 2027-04-27    # any day
"""

import json
import re
from datetime import date, timedelta, timezone
from functools import lru_cache
from pathlib import Path

_PATH = Path(__file__).resolve().parent / "odd_days.json"
_DAYS = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]


def easter(y: int) -> date:
    """Western Easter (the anonymous Gregorian algorithm)."""
    a, b, c = y % 19, y // 100, y % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month, day = divmod(h + l - 7 * m + 114, 31)
    return date(y, month, day + 1)


def nth_weekday(y: int, month: int, weekday: str, n: int) -> date | None:
    """The nth weekday of a month, n = -1 for the last; None when the month
    hasn't one (a 5th Monday)."""
    wd = _DAYS.index(weekday)
    if n < 0:
        last = date(y + month // 12, month % 12 + 1, 1) - timedelta(days=1)
        return last - timedelta(days=(last.weekday() - wd) % 7)
    first = date(y, month, 1)
    day = first + timedelta(days=(wd - first.weekday()) % 7 + 7 * (n - 1))
    return day if day.month == month else None


def last_full_week(y: int, month: int, weekday: str) -> date:
    """That weekday in the month's last full Sunday-to-Saturday week."""
    saturday = nth_weekday(y, month, "SA", -1)
    return saturday - timedelta(days=(5 - _DAYS.index(weekday)) % 7)


def _sun(event: str):
    def when(y: int, tz: str | None) -> date:
        import ephem
        from zoneinfo import ZoneInfo
        moment = getattr(ephem, event)(f"{y}/1/1").datetime().replace(tzinfo=timezone.utc)
        return moment.astimezone(ZoneInfo(tz)).date() if tz else moment.date()
    return when


# The sun's turning points, on the user's own calendar: December 2027's
# solstice is the 22nd in UTC but the evening of the 21st in the US.
SUN = {
    "march_equinox": _sun("next_vernal_equinox"),
    "june_solstice": _sun("next_summer_solstice"),
    "september_equinox": _sun("next_autumn_equinox"),
    "december_solstice": _sun("next_winter_solstice"),
}

ANCHORS = {
    "easter": easter,
    "us_thanksgiving": lambda y: nth_weekday(y, 11, "TH", 4),
    "us_labor_day": lambda y: nth_weekday(y, 9, "MO", 1),
    "us_memorial_day": lambda y: nth_weekday(y, 5, "MO", -1),
    "mothers_day_us": lambda y: nth_weekday(y, 5, "SU", 2),
    "fathers_day_us": lambda y: nth_weekday(y, 6, "SU", 3),
}


def _weekday_from(ref: date, weekday: str, which: str) -> date:
    wd = _DAYS.index(weekday)
    ahead, back = (wd - ref.weekday()) % 7, (ref.weekday() - wd) % 7
    if which == "on_or_after":
        return ref + timedelta(days=ahead)
    if which == "after":
        return ref + timedelta(days=ahead or 7)
    if which == "on_or_before":
        return ref - timedelta(days=back)
    if which == "before":
        return ref - timedelta(days=back or 7)
    if which == "nearest":
        return ref + timedelta(days=ahead) if ahead <= back else ref - timedelta(days=back)
    raise ValueError(f"Unknown which {which!r}")


def _workday(ref: date, which: str) -> date:
    """The working day (Monday to Friday) on, before, after or nearest ref:
    nearest moves a Saturday back to Friday and a Sunday on to Monday."""
    if ref.weekday() < 5:
        return ref
    if which == "on_or_before" or (which == "nearest" and ref.weekday() == 5):
        return ref - timedelta(days=ref.weekday() - 4)
    return ref + timedelta(days=7 - ref.weekday())


def on(rule: dict, y: int, tz: str | None = None) -> date | None:
    """The day a rule falls on in year y; None when it doesn't that year
    (29 February outside a leap year). tz places the sun's turning points."""
    kind = rule["kind"]
    if kind == "fixed":
        try:
            return date(y, rule["month"], rule["day"])
        except ValueError:
            return None
    if kind == "nth":
        return nth_weekday(y, rule["month"], rule["weekday"], rule["n"])
    if kind == "after":
        if "ref" in rule:
            base = on(rule["ref"], y, tz)
        elif rule["anchor"] in SUN:
            base = SUN[rule["anchor"]](y, tz)
        else:
            base = ANCHORS[rule["anchor"]](y)
        return None if base is None else base + timedelta(days=rule["days"])
    if kind == "last_full_week":
        return last_full_week(y, rule["month"], rule["weekday"])
    if kind == "weekday":
        base = on(rule["ref"], y, tz)
        return None if base is None else _weekday_from(base, rule["weekday"], rule["which"])
    if kind == "week_of":
        # That weekday in the Sunday-to-Saturday week holding ref.
        base = on(rule["ref"], y, tz)
        sunday = base - timedelta(days=(base.weekday() + 1) % 7)
        return sunday + timedelta(days=(_DAYS.index(rule["weekday"]) + 1) % 7)
    if kind == "workday":
        base = on(rule["ref"], y, tz)
        return None if base is None else _workday(base, rule["which"])
    if kind == "dates":
        # Set by its organiser each year: only the years someone looked up.
        when = (rule.get("dates") or {}).get(str(y))
        return date.fromisoformat(when) if when else None
    if kind == "day_of_year":
        return date(y, 1, 1) + timedelta(days=rule["n"] - 1)
    raise ValueError(f"Unknown rule {kind!r}")


@lru_cache(maxsize=1)
def _days() -> tuple[dict, ...]:
    return tuple(json.loads(_PATH.read_text(encoding="utf-8"))["days"])


def about(name: str) -> str | None:
    """What the day is for, in a sentence or two, so nobody guesses from its name (11-25: Tie One On Day, which
    is about aprons, was read as a necktie). Written once by a model; the ones it wasn't sure of looked up on the
    web, their source on the row; none where nothing was found."""
    return next((d.get("about") for d in _days() if d["name"] == name), None)


def _same(name: str) -> str:
    """'National Banana Lovers Day' and 'Banana Lovers Day' are one day."""
    name = re.sub(r"(?i)^(national|international|world|global)\s+", "", name)
    return re.sub(r"[^a-z]", "", re.sub(r"(?i)\bday\b", "", name.lower()))


@lru_cache(maxsize=16)
def year(y: int, tz: str | None = None) -> dict[date, tuple[str, ...]]:
    """Every odd day of year y, by date, in time zone tz (UTC when None).
    Worked out once per year and zone per process."""
    found: dict[date, list[str]] = {}
    seen: set[tuple[date, str]] = set()
    for d in _days():
        when = on(d["rule"], y, tz)
        if when is None or when.year != y or (when, _same(d["name"])) in seen:
            continue
        seen.add((when, _same(d["name"])))
        found.setdefault(when, []).append(d["name"])
    return {k: tuple(v) for k, v in found.items()}


def on_day(day: date, tz: str | None = None) -> list[str]:
    return list(year(day.year, tz).get(day, ()))


if __name__ == "__main__":
    import sys
    day = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
    for name in on_day(day):
        print(f"{name}: {about(name) or ''}".rstrip(": "))
