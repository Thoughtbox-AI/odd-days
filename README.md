# Odd days

Nearly 1,900 quirky and unofficial days — Tie One On Day, Morse Code Day, World Tapir Day — each with a rule that dates it for any year and a sentence or two on what it's actually for.

We built and maintain this list for the Daily Brief in [ThoughtBox](https://thoughtbox.ai) — DEMO LINK HERE. Hope you enjoy it too. PRs welcome.

```
$ python odd_days.py 2027-04-27
Marine Mammal Rescue Day: A day created by the California Senate to recognize the people who rescue and care for stranded or injured seals, sea lions, dolphins and whales. …
Morse Code Day: Falls on Samuel Morse's birthday and honors the dot-and-dash code he helped create. People learn a few letters or tap out messages, and ham radio operators often get on the air.
Prime Rib Day: A day for cooking or ordering prime rib, the large roast cut of beef rib.
Tell a Story Day: A day for storytelling. People read stories aloud, share family tales, or tell their own stories.
World Tapir Day: A day for raising awareness of the four tapir species, which are all threatened, and for supporting their conservation.
```

## Why another list

Most lists give you a day's name and this year's date. Names mislead (Tie One On Day is about aprons, not neckties or drinking), and dates move: Black Friday, the day before Thanksgiving, the first Monday after the equinox. So every row here has:

- **`name`**
- **`rule`**: how its date is worked out, so the list is good for any year, not just one
- **`about`**: what the day is for and what people do on it
- **`source` / `about_source`**: where a rule or an about came from, when it wasn't obvious

```json
{"name": "Tie One On Day", "rule": {"kind": "after", "anchor": "us_thanksgiving", "days": -1}, "about": "The day before Thanksgiving, for wearing an apron and giving a gift wrapped in one to someone in need."}
```

## Use it

`odd_days.json` is the list; `odd_days.py` dates it (Python 3.10+, standard library only, plus `pip install ephem` for the few days set by an equinox or solstice).

```python
from datetime import date
import odd_days

odd_days.on_day(date(2026, 11, 25))       # ['Blase’ Day', 'Parfait Day', 'Shopping Reminder Day', 'Tie One On Day']
odd_days.about("Tie One On Day")          # 'The day before Thanksgiving, for wearing an apron …'
odd_days.year(2027)                       # {date: (names, …)} for the whole year
odd_days.on_day(date(2026, 12, 21), "America/New_York")  # the solstice falls on your own calendar
```

## Rules

| kind | means | example |
|---|---|---|
| `fixed` | the same date every year | `{"kind": "fixed", "month": 4, "day": 27}` |
| `nth` | the nth weekday of a month (`n: -1` is the last) | `{"kind": "nth", "month": 11, "weekday": "TH", "n": 4}` |
| `after` | days from an anchor (`easter`, `us_thanksgiving`, `march_equinox`, …) or from another rule (`ref`) | `{"kind": "after", "anchor": "us_thanksgiving", "days": 1}` |
| `weekday` | a weekday `on_or_after`, `after`, `on_or_before`, `before` or `nearest` another rule | the Monday after daylight saving starts |
| `week_of` | that weekday in the Sunday-to-Saturday week holding another rule | |
| `workday` | the working day on, before, after or nearest another rule | |
| `last_full_week` | a weekday in a month's last full week | Administrative Professionals Day |
| `day_of_year` | the nth day of the year | |
| `dates` | announced by its organiser each year: only the years looked up, with a source | Record Store Day |

## Contributing

PRs welcome:

- **A missing day:** add a row with its rule, an `about`, and a `source` if the date or the meaning isn't obvious from a well-known page.
- **An announced day's new year:** add the year to its `dates`, and the page that announced it to `sources`.
- **A wrong about or date:** fix it and say how you know.

Keep `about` to one or two plain sentences: what the day is for and what people do on it, as you'd explain it to a friend. `python -m pytest` checks every rule dates and every row is well formed.

## Credits

The names started from Nate Dimick's [funholidaysapi](https://github.com/NateDimick/funholidaysapi) (MIT), as of 2021. The rules and abouts were labelled by a model (Claude), checked against the dates the source gave for 2021, and the ones it wasn't sure of settled by a web search, with the source kept on the row.

MIT licensed; see [LICENSE](LICENSE).
