#!/usr/bin/env python3
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

TOURNAMENT_ID = "h20260721133003342b93bed415dde43"
TZ_NAME = "America/Chicago"
TZ = ZoneInfo(TZ_NAME)
UTC = ZoneInfo("UTC")


# Known venue addresses. The Tourney field/turf designation is preserved,
# and the street address is appended for better Google Calendar / Maps support.
VENUE_ADDRESSES = {
    "Maple Grove Fernbrook Fields": "14401 99th Avenue N, Maple Grove, MN 55369",
    "Wayzata High School": "4955 Peony Lane N, Plymouth, MN 55446",
    "McMurray Fields-St. Paul": "1155 Jessamine Ave W, Saint Paul, MN 55108",
    "St. Paul Central High School": "275 Lexington Parkway N, Saint Paul, MN 55104",
}

def enrich_location(location):
    """Append a known street address while preserving Tourney's field name."""
    for venue_prefix, address in VENUE_ADDRESSES.items():
        if location.startswith(venue_prefix):
            return f"{location}, {address}"
    return location

TEAMS = [
    {
        "source_name": "Delano JV",
        "calendar_name": "Delano Girls JV",
        "division_id": "h20260803144549719c27a2e4d033b41",
        "team_id": "h202608171758345139f98f800eebc40",
        "slug": "girls-jv",
    },
    {
        "source_name": "Delano Varsity",
        "calendar_name": "Delano Girls Varsity",
        "division_id": "h20260803144549719c27a2e4d033b41",
        "team_id": "h2026081717584362727b0674632334d",
        "slug": "girls-varsity",
    },
    {
        "source_name": "Delano JV (8)",
        "calendar_name": "Delano Boys",
        "division_id": "h202607272226364483dfe2bb6a5944c",
        "team_id": "h202608141203158731248c7422eb541",
        "slug": "boys",
    },
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/152.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
}

def team_url(team):
    return (
        "https://tourneymachine.com/Public/Results/Team.aspx"
        f"?IDTournament={TOURNAMENT_ID}"
        f"&IDDivision={team['division_id']}"
        f"&IDTeam={team['team_id']}"
    )

def get_html(team):
    r = requests.get(team_url(team), headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text

def parse_games(page_html, team):
    soup = BeautifulSoup(page_html, "html.parser")
    games = []

    for row in soup.select("[data-gameid]"):
        values = list(row.stripped_strings)
        if len(values) < 6:
            continue

        game_id = row.get("data-gameid")
        game_no, date_text, time_text, location, team1, team2 = values[:6]

        start = datetime.strptime(
            f"{date_text} {time_text}", "%a %m/%d/%y %I:%M %p"
        ).replace(tzinfo=TZ)

        # GNLL fall schedule uses 50-minute game slots.
        end = start + timedelta(minutes=50)

        if team1 == team["source_name"]:
            opponent = team2
        elif team2 == team["source_name"]:
            opponent = team1
        else:
            # Defensive fallback in case Tourney changes text formatting.
            opponent = team2

        games.append(
            {
                "game_id": game_id,
                "game_no": game_no,
                "calendar_name": team["calendar_name"],
                "source_name": team["source_name"],
                "opponent": opponent,
                "start": start,
                "end": end,
                "location": enrich_location(location),
                "source_url": team_url(team),
                "slug": team["slug"],
            }
        )

    return games

def esc(value):
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\r\n", "\\n")
        .replace("\n", "\\n")
    )

def fold(line, limit=73):
    # Current schedule data is ASCII, so character folding is sufficient here.
    return "\r\n ".join(line[i:i + limit] for i in range(0, len(line), limit))

def make_ics(games, calendar_name):
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Delano GNLL//SportsEngine Tourney Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{esc(calendar_name)}",
        f"X-WR-TIMEZONE:{TZ_NAME}",
        "X-PUBLISHED-TTL:PT1H",
        "REFRESH-INTERVAL;VALUE=DURATION:PT1H",
    ]

    for g in sorted(games, key=lambda x: x["start"]):
        description = (
            f"Game {g['game_no']}\n"
            "2026 GNLL Boys & Girls Sunday Fall League\n"
            f"Source team: {g['source_name']}\n"
            f"SportsEngine Tourney: {g['source_url']}"
        )
        summary = f"{g['calendar_name']} vs {g['opponent']}"

        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{g['game_id']}@gnll-delano",
                f"DTSTAMP:{stamp}",
                f"LAST-MODIFIED:{stamp}",
                f"DTSTART;TZID={TZ_NAME}:{g['start'].strftime('%Y%m%dT%H%M%S')}",
                f"DTEND;TZID={TZ_NAME}:{g['end'].strftime('%Y%m%dT%H%M%S')}",
                f"SUMMARY:{esc(summary)}",
                f"LOCATION:{esc(g['location'])}",
                f"DESCRIPTION:{esc(description)}",
                f"URL:{g['source_url']}",
                "STATUS:CONFIRMED",
                "TRANSP:OPAQUE",
                "END:VEVENT",
            ]
        )

    lines.append("END:VCALENDAR")
    return "\r\n".join(fold(line) for line in lines) + "\r\n"

def write_if_changed(path, content):
    path = Path(path)
    old = path.read_text(encoding="utf-8") if path.exists() else None
    if old == content:
        return False
    path.write_text(content, encoding="utf-8", newline="")
    return True

def main():
    docs = Path("docs")
    permanent = docs / "calendars"
    season = permanent / "gnll-2026-fall"
    archive = docs / "archive" / "gnll" / "2026-fall"
    permanent.mkdir(parents=True, exist_ok=True)
    season.mkdir(parents=True, exist_ok=True)
    archive.mkdir(parents=True, exist_ok=True)

    all_games = []
    by_slug = {}

    for team in TEAMS:
        print(f"Downloading {team['source_name']}...")
        page = get_html(team)
        games = parse_games(page, team)
        if not games:
            raise RuntimeError(f"No games found for {team['source_name']}")
        print(f"{team['source_name']}: {len(games)} games")
        all_games.extend(games)
        by_slug[team["slug"]] = games

    feeds = {
        "delano-lacrosse.ics": make_ics(all_games, "Delano Lacrosse"),
        "delano-girls-jv.ics": make_ics(by_slug["girls-jv"], "Delano Girls JV"),
        "delano-girls-varsity.ics": make_ics(by_slug["girls-varsity"], "Delano Girls Varsity"),
        "delano-boys.ics": make_ics(by_slug["boys"], "Delano Boys"),
    }

    changed = False
    for filename, content in feeds.items():
        # Stable URLs intended for long-term calendar subscriptions.
        changed |= write_if_changed(permanent / filename, content)

        # Current season-specific URLs.
        changed |= write_if_changed(season / filename, content)

        # Archive copies.
        changed |= write_if_changed(archive / filename, content)

    print(f"Wrote {len(all_games)} total events.")
    print("Calendar files changed." if changed else "No calendar changes.")

if __name__ == "__main__":
    main()
