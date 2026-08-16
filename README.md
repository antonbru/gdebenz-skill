# ⛽ ГдеБЕНЗ — навык для ИИ-агентов: где есть бензин рядом

Навык (skill) для ИИ-агентов — **Hermes, OpenClaw, Claude Code, Cline и любых других**. По запросу «где бензин рядом» находит ближайшие АЗС, показывает **наличие бензина 95** (если 95-го нет — можно настроить fallback на 92), **цены** и **свежие комментарии водителей** (очереди, лимиты, что реально есть на колонках).

Данные — краудсорсинговые, с карты [gdebenz.ru](https://gdebenz.ru/) (водители отмечают статусы в реальном времени). Бесплатно, без API-ключа и авторизации.

[![skills.sh](https://skills.sh/badge/antonbru/gdebenz-skill)](https://skills.sh/antonbru/gdebenz-skill)

> 📦 Это **скилл для ИИ-агентов**, а не API-библиотека. Внутри — SKILL.md-инструкция (понимают все агенты) + готовый Python-скрипт без зависимостей. Установка — в разделе ниже.

---

## Возможности

- 🔍 Поиск АЗС по координатам или адресу (адрес → координаты через ваш геокодер)
- ⛽ **Приоритет топлива**: по умолчанию 95, fallback на 92, если 95-го нигде нет
- 💰 Цены 92/95/ДТ со свежестью отметки
- 💬 Комментарии водителей: очереди, лимиты, что наливают
- 🚗 Ссылка **«Построить маршрут»** на Яндекс Картах для каждой станции (от вашей точки до АЗС)
- 📍 Работает из Telegram: можно прислать геолокацию, агент определит точнее
- 🎛 Полная настройка под себя: переменные окружения или правка SKILL.md

## Быстрый старт

Скрипт требует только Python 3 (стандартная библиотека, никаких зависимостей):

```bash
# Ближайшие АЗС с 95-м бензином рядом с Красной площадью (радиус 5 км)
python3 skills/gdebenz-api/scripts/nearest_stations.py 55.7539 37.6208
```

Пример вывода:

```
Найдено АЗС: 10 (радиус 5.0 км), топливо 95
   1.51 км | ✅ Роснефть | Котельническая набережная, 1/15 соор10 | топливо: 92,95 | 92=65.05 95=71.25 | 🚗 https://yandex.ru/maps/?rtext=55.7539,37.6208~55.7464,37.6409&rtt=auto
   2.74 км | ✅ Лукойл   | ул Коровий Вал, 9А                    | топливо: 92,95,ДТ | 92=62.5 95=74.79 ⚠️очередь | 🚗 https://yandex.ru/maps/?rtext=55.7539,37.6208~55.7294,37.6171&rtt=auto
   ...

Свежие комментарии водителей:
  Лукойл (2.74 км):
    • 92, 95 · Очередь ≈20–50 машин — 2026-08-16 06:18:29 (на месте)
```

Ссылка 🚗 — «Построить маршрут» в Яндекс Картах: открывается маршрут от вашей точки до АЗС.

## Установка для агентов

### Hermes Agent

```bash
# Через tap (рекомендуется)
hermes skills tap add antonbru/gdebenz-skill
hermes skills install gdebenz-api

# Или напрямую клонированием
git clone https://github.com/antonbru/gdebenz-skill.git
bash gdebenz-api/scripts/install.sh --agent hermes
```

### OpenClaw

```bash
# Глобально для всех агентов OpenClaw
openclaw skills install antonbru/gdebenz-skill --global

# Или вручную: скопировать папку в ~/.openclaw/skills/
git clone https://github.com/antonbru/gdebenz-skill.git
cp -r gdebenz-api/skills/gdebenz-api ~/.openclaw/skills/
```

> OpenClaw использует `~/.openclaw/skills/` (не `~/.claude/skills/`). Формат SKILL.md тот же.

### Claude Code

```bash
# Через skills.sh
npx skills add antonbru/gdebenz-skill -a claude-code

# Или вручную
git clone https://github.com/antonbru/gdebenz-skill.git
cp -r gdebenz-api/skills/gdebenz-api ~/.claude/skills/
```

### Cline, Cursor, Codex и другие

Универсальный способ — [skills.sh](https://skills.sh) (поддерживает Claude Code, Cursor, Codex, Gemini CLI, GitHub Copilot, Windsurf, Cline, Roo Code, OpenCode):

```bash
npx skills add antonbru/gdebenz-skill -a cline      # пример для Cline
npx @skill-hub/cli install gdebenz-api --agent cline
```

Или скопируйте папку `skills/gdebenz-api/` в директорию скиллов вашего агента (обычно `~/.<agent>/skills/`).

### Любой LLM-агент (универсально)

Просто добавьте содержимое [`skills/gdebenz-api/SKILL.md`](skills/gdebenz-api/SKILL.md) в системный промпт или базу знаний агента — это самодостаточная инструкция.

### Автоустановка скриптом

```bash
bash scripts/install.sh                # определит агента автоматически
bash scripts/install.sh --agent openclaw
bash scripts/install.sh --agent hermes --dir ~/custom/path
```

## Настройка под себя

Всё конфигурируется. Два способа:

**1. Переменные окружения** (для скрипта и агента):

| Переменная | По умолчанию | Что делает |
|---|---|---|
| `GB_API_FUEL` | `95` | Приоритетное топливо: `92`, `95`, `ДТ` |
| `GB_API_FALLBACK` | `92` | Запасное топливо, если основного нет. Пусто = без fallback |
| `GB_API_RADIUS` | `5` | Радиус поиска, км |
| `GB_API_TOP_N` | `8` | Сколько станций показывать |
| `GB_API_COMMENTS` | `1` | Комментарии водителей (`0` = выключить) |
| `GB_API_COMMENT_N` | `5` | Для скольких станций тянуть комментарии |
| `GB_API_MAPS` | `1` | Ссылка «Построить маршрут» (Яндекс Карты) (`0` = выключить) |

```bash
GB_API_FUEL=ДТ GB_API_RADIUS=10 GB_API_COMMENTS=0 python3 skills/gdebenz-api/scripts/nearest_stations.py 55.7539 37.6208
```

**2. Правка SKILL.md** — откройте [`skills/gdebenz-api/SKILL.md`](skills/gdebenz-api/SKILL.md), секция «Приоритеты (по умолчанию)», и поменяйте под себя: другое топливо, другой радиус, показывать/не показывать комментарии. Агент будет следовать тому, что написано в скилле.

Подробнее — в [`docs/customizing.md`](docs/customizing.md), готовый шаблон — [`config.example.yaml`](config.example.yaml).

## API (кратко)

Без авторизации, JSON, заголовки `User-Agent` + `Referer: https://gdebenz.ru/`.

| Эндпоинт | Описание |
|---|---|
| `GET /api/stations?lat1=&lon1=&lat2=&lon2=` | АЗС в прямоугольнике (главный) |
| `GET /api/comments/{osm_id}/recent?limit=12` | Последние комментарии станции |
| `GET /api/comments?lat1=&lon1=&lat2=&lon2=` | Сводка отметок по области |
| `GET /api/cities?q=` | Поиск города (lat/lon) |

Геокодер адресов на сайте отключён (404) — для «адрес → координаты» используйте Яндекс.Геокодер или OSM Nominatim.

## Важно знать

- ⚠️ Данные **краудсорсинговые**: статус «нет бензина» может быть устаревшим. Всегда показывается свежесть отметки/цены.
- Поля: `status` (`yes`/`no`/`null` — null значит «нет отметки», не «нет бензина»), `fuels_now` (какое топливо есть), `conflict` (`queue` — очередь), `prices_now` (цены со временем отметки).
- Внутри bbox может быть 100+ станций — скрипт показывает топ-N по расстоянию.

## Лицензия

MIT — можно использовать, менять и распространять свободно. См. [LICENSE](LICENSE).

---

*Навык «ГдеБЕНЗ» — поиск АЗС, бензин 95, бензин рядом, заправка поблизости, цены на бензин, очереди на АЗС, gdebenz.ru. Работает в Hermes, OpenClaw, Claude Code, Cline и других ИИ-агентах.*
