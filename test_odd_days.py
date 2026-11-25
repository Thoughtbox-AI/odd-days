"""The odd-day list and the rules that date it (the brief's "Today is ...")."""

from datetime import date

import pytest

import odd_days


@pytest.mark.parametrize("y,expected", [(2021, date(2021, 4, 4)), (2026, date(2026, 4, 5)), (2027, date(2027, 3, 28))])
def test_easter(y, expected):
    assert odd_days.easter(y) == expected


def test_weekday_rules():
    assert odd_days.nth_weekday(2026, 11, "TH", 4) == date(2026, 11, 26)  # US Thanksgiving
    assert odd_days.nth_weekday(2026, 10, "SU", -1) == date(2026, 10, 25)
    assert odd_days.nth_weekday(2026, 6, "MO", 5) == date(2026, 6, 29)
    assert odd_days.nth_weekday(2026, 2, "MO", 5) is None  # no fifth Monday
    # The Wednesday of April's last full week: 2021's was the 21st, 2026's the 22nd.
    assert odd_days.last_full_week(2021, 4, "WE") == date(2021, 4, 21)
    assert odd_days.last_full_week(2026, 4, "WE") == date(2026, 4, 22)


def test_29_february_is_only_in_a_leap_year():
    assert odd_days.on({"kind": "fixed", "month": 2, "day": 29}, 2026) is None
    assert odd_days.on({"kind": "fixed", "month": 2, "day": 29}, 2028) == date(2028, 2, 29)


def test_every_rule_in_the_list_works_out_and_every_date_has_a_day():
    for y in range(2024, 2036):
        assert len(odd_days.year(y)) >= 365


def test_moving_days_move():
    names = lambda d: odd_days.on_day(d)
    assert "Black Friday" in names(date(2026, 11, 27)) and "Cyber Monday" in names(date(2026, 11, 30))
    assert "Administrative Professionals Day" in names(date(2026, 4, 22))
    assert "Mother-In-Law Day" in names(date(2026, 10, 25))
    assert "Hug A Bear Day" in names(date(2026, 11, 7))
    assert "A Blue Christmas" in names(date(2026, 12, 21)) and "A Blue Christmas" not in names(date(2026, 11, 27))


def test_a_day_named_twice_shows_once():
    for when, days in odd_days.year(2026).items():
        keys = [odd_days._same(n) for n in days]
        assert len(keys) == len(set(keys)), when





def test_days_set_by_the_sun_fall_on_the_users_own_calendar():
    blue = {"kind": "after", "anchor": "december_solstice", "days": 0}
    # 2027's solstice is 02:41 UTC on the 22nd: still the 21st in New York.
    assert odd_days.on(blue, 2027) == date(2027, 12, 22)
    assert odd_days.on(blue, 2027, "America/New_York") == date(2027, 12, 21)
    sleep = {"kind": "weekday", "weekday": "FR", "which": "before", "ref": {"kind": "after", "anchor": "march_equinox", "days": 0}}
    assert odd_days.on(sleep, 2026, "America/New_York") == date(2026, 3, 13)  # the equinox is itself a Friday


@pytest.mark.parametrize("rule,y,expected", [
    ({"kind": "weekday", "weekday": "SA", "which": "nearest", "ref": {"kind": "fixed", "month": 5, "day": 10}}, 2021, date(2021, 5, 8)),
    ({"kind": "week_of", "weekday": "TH", "ref": {"kind": "fixed", "month": 2, "day": 22}}, 2021, date(2021, 2, 25)),
    ({"kind": "workday", "which": "nearest", "ref": {"kind": "fixed", "month": 10, "day": 16}}, 2021, date(2021, 10, 15)),
    ({"kind": "workday", "which": "nearest", "ref": {"kind": "fixed", "month": 10, "day": 16}}, 2022, date(2022, 10, 17)),
    ({"kind": "workday", "which": "on_or_after", "ref": {"kind": "fixed", "month": 11, "day": 2}}, 2025, date(2025, 11, 3)),
    ({"kind": "day_of_year", "n": 256}, 2028, date(2028, 9, 12)),
    ({"kind": "after", "days": -6, "ref": {"kind": "nth", "month": 5, "weekday": "WE", "n": 1}}, 2021, date(2021, 4, 29)),
    ({"kind": "weekday", "weekday": "MO", "which": "after", "ref": {"kind": "nth", "month": 3, "weekday": "SU", "n": 2}}, 2026, date(2026, 3, 9)),
])
def test_rules_built_on_other_days(rule, y, expected):
    assert odd_days.on(rule, y) == expected


def test_an_announced_day_shows_only_in_the_years_looked_up():
    rule = {"kind": "dates", "dates": {"2027": "2027-03-20"}}
    assert odd_days.on(rule, 2027) == date(2027, 3, 20)
    assert odd_days.on(rule, 2028) is None
    assert "Corn Dog Day" in odd_days.on_day(date(2027, 3, 20))


def test_a_day_says_what_its_for():
    # Tie One On Day is aprons, not neckties.
    assert "apron" in odd_days.about("Tie One On Day")
    assert odd_days.about("No Such Day") is None


def test_every_row_is_well_formed():
    names = set()
    for d in odd_days._days():
        assert set(d) <= {"name", "rule", "about", "source", "sources", "about_source"}, d["name"]
        assert d["name"] not in names, d["name"]
        names.add(d["name"])
        odd_days.on(d["rule"], 2026)  # a rule that doesn't parse raises
