#!/usr/bin/env python3
"""Ближайшие АЗС из gdebenz.ru (краудсорс-данные, могут быть устаревшими).

Настройка под себя — через переменные окружения (или CLI-аргументы, они приоритетнее):

    GB_API_FUEL        приоритетное топливо              (default: 95)
    GB_API_FALLBACK    запасное, если нет основного      (default: 92; пусто = без fallback)
    GB_API_RADIUS      радиус поиска, км                 (default: 5)
    GB_API_TOP_N       сколько станций показать          (default: 8)
    GB_API_COMMENTS    показывать комментарии водителей  (default: 1; 0 = выключить)
    GB_API_COMMENT_N   сколько станций с комментариями   (default: 5)
    GB_API_MAPS        ссылка «Построить маршрут» (Яндекс Карты) (default: 1; 0 = выключить)

Примеры:
    GB_API_FUEL=95 python3 nearest_stations.py 55.7539 37.6208
    GB_API_FUEL=92 GB_API_RADIUS=10 python3 nearest_stations.py 55.7539 37.6208
    python3 nearest_stations.py 55.7539 37.6208 8 95     # CLI перекрывает env

Проверено на живом API (Москва): 114 станций в bbox ~11x11 км.
"""
import argparse
import json
import math
import os
import sys
import urllib.request

UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://gdebenz.ru/"}
API = "https://gdebenz.ru/api/stations"
COMMENTS_API = "https://gdebenz.ru/api/comments"


def env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def fetch(url: str):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def recent_comments(osm_id: str, limit: int = 12):
    """Последние комментарии станции: [{status, detail, created_at, on_site}, ...]"""
    try:
        d = fetch(f"{COMMENTS_API}/{osm_id}/recent?limit={limit}")
        return d if isinstance(d, list) else []
    except Exception:
        return []


def build_rows(lat0: float, lon0: float, stations: list, fuel: str | None, radius_km: float):
    rows = []
    for s in stations:
        d = haversine_km(lat0, lon0, s["lat"], s["lon"])
        if d > radius_km:
            continue
        fuels_now = s.get("fuels_now") or ""
        if fuel and fuel not in fuels_now:
            continue
        prices = s.get("prices_now", {})
        p92 = prices.get("92", {}).get("p") if prices.get("92") else None
        p95 = prices.get("95", {}).get("p") if prices.get("95") else None
        t = None
        for f in ("92", "95", "ДТ"):
            if prices.get(f) and prices[f].get("t"):
                t = prices[f]["t"]
                break
        rows.append({
            "d": d,
            "osm_id": s.get("osm_id"),
            "name": s.get("name", "?"),
            "addr": s.get("addr", ""),
            "status": s.get("status"),
            "fuels": fuels_now,
            "p92": p92,
            "p95": p95,
            "t": t,
            "conflict": s.get("conflict"),
            "lat": s.get("lat"),
            "lon": s.get("lon"),
        })
    rows.sort(key=lambda r: r["d"])
    return rows


def yandex_maps_url(lat0: float, lon0: float, lat: float, lon: float) -> str:
    """Ссылка «Построить маршрут» в Яндекс Картах от точки пользователя до АЗС."""
    return (f"https://yandex.ru/maps/?rtext={lat0:.4f},{lon0:.4f}~{lat:.4f},{lon:.4f}&rtt=auto")


def print_rows(rows, top_n: int, maps_on: bool, lat0: float = None, lon0: float = None):
    for r in rows[:top_n]:
        status = {"yes": "✅", "no": "❌"}.get(r["status"], "—")
        warn = " ⚠️очередь" if r["conflict"] else ""
        fresh = f" (отм. {r['t']})" if r["t"] else ""
        route = ""
        if maps_on and r.get("lat") is not None and lat0 is not None:
            route = " | 🚗 " + yandex_maps_url(lat0, lon0, r["lat"], r["lon"])
        print(f"  {r['d']:5.2f} км | {status} {r['name']:<18s} | {r['addr']:<32s} | "
              f"топливо: {r['fuels'] or '—':10s} | 92={r['p92']} 95={r['p95']}{fresh}{warn}{route}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Ближайшие АЗС из gdebenz.ru")
    ap.add_argument("lat", type=float)
    ap.add_argument("lon", type=float)
    ap.add_argument("radius_km", type=float, nargs="?", default=None)
    ap.add_argument("fuel", nargs="?", default=None, help="напр. 92, 95, ДТ (перекрывает GB_API_FUEL)")
    args = ap.parse_args()

    radius = args.radius_km if args.radius_km is not None else float(os.environ.get("GB_API_RADIUS", 5))
    fuel = args.fuel or os.environ.get("GB_API_FUEL", "95") or None
    fallback = os.environ.get("GB_API_FALLBACK", "92") or None
    top_n = env_int("GB_API_TOP_N", 8)
    comments_on = os.environ.get("GB_API_COMMENTS", "1") != "0"
    comment_n = env_int("GB_API_COMMENT_N", 5)
    maps_on = os.environ.get("GB_API_MAPS", "1") != "0"

    # bbox: delta по широте ~= radius/111 км; по долготе зависит от широты — берём с запасом
    dlat = radius / 111.0
    dlon = radius / (111.0 * max(math.cos(math.radians(args.lat)), 0.2))
    url = f"{API}?lat1={args.lat - dlat}&lon1={args.lon - dlon}&lat2={args.lat + dlat}&lon2={args.lon + dlon}"
    stations = fetch(url)
    if not isinstance(stations, list):
        print(f"Ошибка API: {stations}", file=sys.stderr)
        return 1

    # Приоритет: основное топливо; если совсем нет — fallback
    used_fuel = fuel
    fallback_used = False
    rows = build_rows(args.lat, args.lon, stations, fuel, radius)
    if not rows and fallback:
        used_fuel = fallback
        fallback_used = True
        rows = build_rows(args.lat, args.lon, stations, fallback, radius)

    if not rows:
        print("АЗС не найдено в радиусе", radius, "км" + (f" с топливом {fuel}" if fuel else ""))
        return 0

    print(f"Найдено АЗС: {len(rows)} (радиус {radius} км)"
          + (f", топливо {used_fuel}" if used_fuel else "")
          + (" — ⚠️ основного топлива нет, показываю запасное" if fallback_used else ""))
    print_rows(rows, top_n, maps_on, args.lat, args.lon)

    if comments_on:
        print("\nСвежие комментарии водителей:")
        for r in rows[:comment_n]:
            comments = recent_comments(r["osm_id"])
            fresh = [c for c in comments if c.get("detail")][:2]
            if fresh:
                print(f"  {r['name']} ({r['d']:.2f} км):")
                for c in fresh:
                    on_site = " (на месте)" if c.get("on_site") else ""
                    print(f"    • {c.get('detail')} — {c.get('created_at')}{on_site}")
            else:
                print(f"  {r['name']} ({r['d']:.2f} км): комментариев нет")
    return 0


if __name__ == "__main__":
    sys.exit(main())
