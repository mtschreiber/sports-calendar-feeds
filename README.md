# Sports Calendar Feeds

This repository publishes automatically updated sports calendar feeds in standard
iCalendar (`.ics`) format.

## Current scope

The project is currently configured specifically for the:

**2026 GNLL Boys & Girls Sunday Fall League**

The current data source is **SportsEngine Tourney / Tourney Machine**. The generator
reads the live public schedule pages for the configured Delano teams, normalizes the
schedule data, adds known venue street addresses, and publishes subscribable `.ics`
calendar feeds.

This repository is intentionally named `sports-calendar-feeds` so it can later grow
to support additional tournaments, seasons, teams, sports, and schedule providers
without renaming the repository.

## Current calendars

The tournament-specific subscription feeds are published under:

`/calendars/gnll-2026-fall/`

Available feeds:

- `/calendars/gnll-2026-fall/delano-lacrosse.ics` — all three Delano teams
- `/calendars/gnll-2026-fall/delano-girls-jv.ics`
- `/calendars/gnll-2026-fall/delano-girls-varsity.ics`
- `/calendars/gnll-2026-fall/delano-boys.ics`

For the GitHub Pages site, the full URLs are:

- `https://mtschreiber.github.io/sports-calendar-feeds/calendars/gnll-2026-fall/delano-lacrosse.ics`
- `https://mtschreiber.github.io/sports-calendar-feeds/calendars/gnll-2026-fall/delano-girls-jv.ics`
- `https://mtschreiber.github.io/sports-calendar-feeds/calendars/gnll-2026-fall/delano-girls-varsity.ics`
- `https://mtschreiber.github.io/sports-calendar-feeds/calendars/gnll-2026-fall/delano-boys.ics`

These URLs can be added to Google Calendar using:

**Other calendars -> + -> From URL**

They can also be used as subscribed calendars in Apple Calendar.

## Team display names

SportsEngine Tourney currently identifies the teams as:

- `Delano JV`
- `Delano Varsity`
- `Delano JV (8)`

The published calendars display them as:

- `Delano Girls JV`
- `Delano Girls Varsity`
- `Delano Boys`

Opponent names are preserved as Tourney provides them.

## Venue addresses

Known venue addresses are appended to Tourney's field designation so calendar apps
can provide better map and navigation support.

For example:

`Maple Grove Fernbrook Fields - Turf 1S, 14401 99th Avenue N, Maple Grove, MN 55369`

If a future venue is not yet mapped, the original Tourney location is preserved.

## Automatic updates

The GitHub Actions workflow runs approximately once per hour.

Each run:

1. Downloads the current schedule for the configured teams.
2. Parses and normalizes the games.
3. Regenerates the `.ics` files.
4. Commits the files only if the generated calendar data changed.

Tourney's game ID is used as the iCalendar event `UID`, which helps calendar clients
associate a changed game with the same existing event instead of treating it as a
brand-new game.

Google Calendar controls how often it refreshes externally subscribed `.ics` feeds,
so a Tourney change may not appear in Google Calendar immediately even after this
repository has updated.

## Archive

Season-specific copies are also stored under:

`/archive/gnll/2026-fall/`

This makes it possible to retain historical calendar files while adding future
tournaments and seasons.

## Future expansion

The repository structure is intended to support additional calendar groups such as:

- other GNLL seasons
- other lacrosse tournaments
- hockey schedules
- basketball schedules
- other SportsEngine Tourney events
- other schedule providers

A future tournament could simply receive another folder, for example:

`/calendars/gnll-2027-spring/`

or:

`/calendars/hockey-2026-27/`

without affecting existing tournament-specific subscriptions.

## Local generator test

Install the required Python packages:

    python -m pip install -r requirements.txt

Then run:

    python generate_calendar.py

Generated calendar files are written under the `docs` directory.
