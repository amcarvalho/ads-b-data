import argparse
from typing import Any, Dict, List, Optional

import requests


DEFAULT_FEEDER_URL = "http://192.168.1.78:8080/data/aircraft.json"
ADSBDB_CALLSIGN_ENDPOINT = "https://api.adsbdb.com/v0/callsign"
ADSBLOL_ROUTESET_ENDPOINT = "https://api.adsb.lol/api/0/routeset"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Test route enrichment using live UltraFeeder data."
    )
    parser.add_argument(
        "--feeder-url",
        default=DEFAULT_FEEDER_URL,
        help=f"UltraFeeder aircraft JSON endpoint (default: {DEFAULT_FEEDER_URL})",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Max number of aircraft/callsigns to test.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="HTTP timeout in seconds.",
    )
    return parser.parse_args()


def fetch_live_aircraft(feeder_url: str, timeout: int) -> List[Dict[str, Any]]:
    response = requests.get(feeder_url, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    aircraft = payload.get("aircraft", [])
    if not isinstance(aircraft, list):
        raise ValueError("Unexpected feeder response: `aircraft` is not a list.")
    return aircraft


def pick_candidates(aircraft: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []
    for entry in aircraft:
        callsign = (entry.get("flight") or "").strip()
        if not callsign:
            continue
        lat = entry.get("lat")
        lon = entry.get("lon")
        if lat is None or lon is None:
            continue
        candidates.append(
            {
                "callsign": callsign,
                "hex": entry.get("hex"),
                "registration": entry.get("r"),
                "lat": lat,
                "lng": lon,
            }
        )
        if len(candidates) >= limit:
            break
    return candidates


def lookup_adsbdb_route(callsign: str, timeout: int) -> Dict[str, Optional[str]]:
    url = f"{ADSBDB_CALLSIGN_ENDPOINT}/{callsign}"
    response = requests.get(url, timeout=timeout)
    if response.status_code == 404:
        return {
            "status": "not_found",
            "dep_code": None,
            "dep_city": None,
            "dep_country": None,
            "arr_code": None,
            "arr_city": None,
            "arr_country": None,
        }
    response.raise_for_status()

    try:
        route = response.json().get("response", {}).get("flightroute")
    except ValueError:
        return {
            "status": "bad_json",
            "dep_code": None,
            "dep_city": None,
            "dep_country": None,
            "arr_code": None,
            "arr_city": None,
            "arr_country": None,
        }
    if not route:
        return {
            "status": "no_route",
            "dep_code": None,
            "dep_city": None,
            "dep_country": None,
            "arr_code": None,
            "arr_city": None,
            "arr_country": None,
        }

    origin = route.get("origin", {}) or {}
    destination = route.get("destination", {}) or {}
    return {
        "status": "ok",
        "dep_code": origin.get("icao_code") or origin.get("iata_code"),
        "dep_city": origin.get("municipality"),
        "dep_country": origin.get("country_name"),
        "arr_code": destination.get("icao_code") or destination.get("iata_code"),
        "arr_city": destination.get("municipality"),
        "arr_country": destination.get("country_name"),
    }


def probe_adsblol_routeset(candidates: List[Dict[str, Any]], timeout: int) -> None:
    body = {"planes": [{"callsign": c["callsign"], "lat": c["lat"], "lng": c["lng"]} for c in candidates]}
    response = requests.post(ADSBLOL_ROUTESET_ENDPOINT, json=body, timeout=timeout)
    print("\nadsb.lol routeset probe:")
    print(f"  HTTP {response.status_code}, content-type={response.headers.get('content-type')}, bytes={len(response.text)}")
    if response.text.strip():
        print(f"  body sample: {response.text[:200]}")
    else:
        print("  empty response body")


def main() -> int:
    args = parse_args()

    try:
        aircraft = fetch_live_aircraft(args.feeder_url, args.timeout)
    except Exception as exc:
        print(f"Failed to fetch feeder data: {exc}")
        return 1

    candidates = pick_candidates(aircraft, args.limit)
    if not candidates:
        print("No candidate aircraft with callsign+position found.")
        return 2

    print(f"Fetched {len(aircraft)} aircraft; testing {len(candidates)} callsigns:\n")
    print(f"{'callsign':<10} {'hex':<8} {'reg':<10} {'dep':<8} {'arr':<8} {'dep_city':<18} {'arr_city':<18} {'status':<10}")
    print("-" * 110)

    success = 0
    for candidate in candidates:
        route = lookup_adsbdb_route(candidate["callsign"], args.timeout)
        if route["status"] == "ok":
            success += 1
        print(
            f"{candidate['callsign']:<10} "
            f"{str(candidate.get('hex') or '-'): <8} "
            f"{str(candidate.get('registration') or '-'): <10} "
            f"{str(route.get('dep_code') or '-'): <8} "
            f"{str(route.get('arr_code') or '-'): <8} "
            f"{str(route.get('dep_city') or '-'): <18} "
            f"{str(route.get('arr_city') or '-'): <18} "
            f"{route['status']:<10}"
        )

    print(f"\nADSBDB route success: {success}/{len(candidates)}")

    try:
        probe_adsblol_routeset(candidates, args.timeout)
    except Exception as exc:
        print(f"\nadsb.lol routeset probe failed: {exc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
