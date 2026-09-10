# Sports Calendar Feeds

Automatically updated, publicly subscribable sports calendar feeds.

## Permanent subscription paths

These paths are deliberately season/tournament independent:

- `/calendars/delano-lacrosse.ics`
- `/calendars/delano-girls-jv.ics`
- `/calendars/delano-girls-varsity.ics`
- `/calendars/delano-boys.ics`

The generator currently populates them from the 2026 GNLL Boys & Girls Sunday Fall League.
Opponent names are preserved exactly as SportsEngine Tourney publishes them.

Season-specific copies are also written under:

`/archive/gnll/2026-fall/`

## GitHub Pages setup

After uploading this repository:

1. Go to Settings -> Pages.
2. Choose `Deploy from a branch`.
3. Select branch `main` and folder `/docs`.
4. Save.
5. Open Actions and manually run `Update GNLL calendars` once.

The workflow then checks SportsEngine Tourney approximately hourly and commits only
when generated calendar content changes.

For the `mtschreiber/sports-calendar-feeds` repository, the permanent combined feed
will be:

`https://mtschreiber.github.io/sports-calendar-feeds/calendars/delano-lacrosse.ics`

## Apple Calendar

Subscribe to the HTTPS feed URL rather than importing the `.ics` file. This allows
future schedule changes to appear through the same stable URL.
