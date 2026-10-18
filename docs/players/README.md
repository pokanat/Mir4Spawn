# MIR4 Observatory

Public panel: https://pokanat.github.io/Mir4Spawn/players/

A buildless panel using official public all-server rankings. No Mirkit premium endpoints or history are used. The existing boss tracker remains at the root.

## Data collection

`scripts/collect_rankings.py` fetches the official ranking and the nine pagination URLs advertised by that page. All 1,000 ranks must be present and unique before writing. Failures leave the previous file intact. The scheduled GitHub workflow runs every two hours at minute 23 and can also be started with **Actions → Update official MIR4 player rankings → Run workflow**. GitHub schedules can be delayed or disabled after repository inactivity; inspect Actions if capture dates stop advancing.

Distinct ranking datasets become snapshots; identical results only update `checkedAt`. The latest 90 snapshots are retained. These are observed snapshots, not an all-time archive, and may represent a source ranking older than the fetch time. The UI shows both dates.

The page fetches `data.json` from the public repository's raw endpoint, with the deployed copy as a labeled fallback. This allows ranking commits made by GitHub Actions to be read even when those commits do not trigger GitHub Pages builds. No credentials are sent to visitors.

## Identity and limitations

The official ranking does not expose a stable character ID. Profiles use unique exact-name matches; possible transfers compare names unique in both adjacent captures. Names can be reused, so changes are unverified. Renames are never inferred. Disappearance from the top 1,000 is not interpreted as a transfer or deletion.

Level, old names, detailed combat stats and market price history are not available from this source. Favorites are browser-local. CSV exports include only the filtered collected players, not unavailable tracked names.

## Local maintenance

Run `python scripts/collect_rankings.py` from the repository. Python standard library only. Frontend syntax check: `node --check docs/players/app.js`.
