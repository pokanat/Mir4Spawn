"""Collect only the official public all-server ranking; never merge renamed players.
All ten pages must pass validation before replacing the last good dataset.
"""
import datetime as dt
import hashlib
import html
import json
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'docs/players/data.json'
SOURCE = 'https://cs.mir4global.com/rank?ranktype=1'

def clean(value):
    return html.unescape(re.sub('<[^>]+>', '', value)).strip()

def parse_page(raw):
    players = []
    for row in re.findall(r'<tr\b[^>]*class=["\'][^"\']*list_article[^"\']*["\'][^>]*>(.*?)</tr>', raw, re.S):
        cells = re.findall(r'<td\b[^>]*>(.*?)</td>', row, re.S)
        if len(cells) != 5:
            raise ValueError('Unexpected ranking columns')
        rank = re.search(r'class=["\']num["\'][^>]*>([\d,]+)', cells[0])
        name = re.search(r'class=["\']user_name["\'][^>]*>(.*?)</span>', cells[1], re.S)
        if not rank or not name:
            raise ValueError('Missing rank or character name')
        players.append(dict(rank=int(rank[1].replace(',', '')), name=clean(name[1]), server=clean(cells[2]), clan=clean(cells[3]), power=int(clean(cells[4]).replace(',', ''))))
    if not players:
        raise ValueError('No ranking rows; previous data preserved')
    return players

def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'MIR4PlayerPanel/1.0 public-ranking-reader'})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode('utf-8')

def save(players, raw, scope):
    players.sort(key=lambda p: p['rank'])
    if len({p['rank'] for p in players}) != len(players) or any(p['power'] <= 0 for p in players):
        raise ValueError('Invalid or duplicate ranks')
    dates = re.findall(r'The ranking\s*\[\s*([\d.]+)\s*\]', raw)
    observed = dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
    digest = hashlib.sha256(json.dumps(players, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    old = json.loads(DEST.read_text()) if DEST.exists() else {}
    snapshots = old.get('snapshots', [])
    if not snapshots or snapshots[-1]['digest'] != digest:
        snapshots.append({'observedAt': observed, 'sourceDate': dates[0] if dates else None, 'digest': digest, 'players': players})
    result = {'source': SOURCE, 'checkedAt': observed, 'scope': scope, 'retention': 90, 'snapshots': snapshots[-90:]}
    DEST.parent.mkdir(parents=True, exist_ok=True)
    tmp = DEST.with_suffix('.tmp')
    tmp.write_text(json.dumps(result, ensure_ascii=False, separators=(',', ':')))
    tmp.replace(DEST)
    print(f'Saved {len(players)} players; {len(result["snapshots"])} distinct snapshots')

if __name__ == '__main__':
    raw = fetch(SOURCE)
    players = parse_page(raw)
    for page in range(2, 11):
        rows = parse_page(fetch(SOURCE + f'&liststyle=ol&page={page}'))
        if [p['rank'] for p in rows] != list(range((page-1)*100+1, page*100+1)):
            raise ValueError(f'Incomplete page {page}; previous dataset preserved')
        players.extend(rows)
    if [p['rank'] for p in players] != list(range(1, 1001)):
        raise ValueError('Incomplete top 1000; previous dataset preserved')
    save(players, raw, 'Official all-server top 1,000')
