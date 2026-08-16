# ⛽ GdeBenz — AI agent skill: find gas stations with fuel nearby

A skill for AI agents — **Hermes, OpenClaw, Claude Code, Cline and any other**. On request «where is gas nearby» it finds nearest gas stations (АЗС) in Russia, shows **fuel availability (prefers 95, optional fallback to 92)**, **prices** and **fresh driver comments** (queues, limits).

Data is crowdsourced from [gdebenz.ru](https://gdebenz.ru/) (drivers update statuses in real time). Free, no API key, no auth.

## Features

- Find stations by coordinates or address (address → coords via your own geocoder)
- Fuel priority: default 95, fallback 92
- Prices for 92/95/ДТ with freshness timestamps
- Driver comments: queues, limits, what's actually available
- Works from Telegram: user can send location
- Fully configurable via env vars or SKILL.md edit

## Quick start

```bash
# Nearest stations with 95 fuel near Red Square (5 km radius)
python3 skills/gdebenz-api/scripts/nearest_stations.py 55.7539 37.6208
```

Python 3 only, standard library, no dependencies.

## Install

### Hermes
```bash
hermes skills tap add antonbru/gdebenz-skill
hermes skills install gdebenz-api
```

### OpenClaw
```bash
openclaw skills install antonbru/gdebenz-skill --global
# or manually:
cp -r skills/gdebenz-api ~/.openclaw/skills/
```

### Claude Code
```bash
npx skills add antonbru/gdebenz-skill -a claude-code
# or manually:
cp -r skills/gdebenz-api ~/.claude/skills/
```

### Any agent (universal)
Add `skills/gdebenz-api/SKILL.md` to your agent's system prompt or knowledge base — it's self-contained.

## Configuration

Env vars (defaults):

| Var | Default | Description |
|---|---|---|
| `GB_API_FUEL` | `95` | Preferred fuel: `92`, `95`, `ДТ` |
| `GB_API_FALLBACK` | `92` | Fallback fuel if primary is nowhere. Empty = no fallback |
| `GB_API_RADIUS` | `5` | Search radius, km |
| `GB_API_TOP_N` | `8` | How many stations to show |
| `GB_API_COMMENTS` | `1` | Show driver comments (`0` = off) |
| `GB_API_COMMENT_N` | `5` | How many stations get comments |

Or edit the «Приоритеты (по умолчанию)» section in `skills/gdebenz-api/SKILL.md`.

## Important

⚠️ Data is **crowdsourced**: a «no fuel» status may be outdated. Freshness timestamps are always shown.
`status`: `yes`/`no`/`null` (null = no marking, not «no fuel»). `fuels_now`: comma-separated fuel list. `conflict`: `queue`.

## License

MIT — free to use, modify, distribute. See [LICENSE](LICENSE).
