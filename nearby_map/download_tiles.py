#!/usr/bin/env python3
"""Download GSI XYZ tiles for offline map with flexible collection policy."""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
CFG = HERE / "config.json"
RETRY_MAX = 3
RETRY_DELAY = 1.0


def lon2tilex(lon: float, z: int) -> int:
    return int((lon + 180.0) / 360.0 * (2**z))


def lat2tiley(lat: float, z: int) -> int:
    lat_rad = math.radians(lat)
    n = math.log(math.tan(math.pi / 4 + lat_rad / 2))
    return int((1 - n / math.pi) / 2 * (2**z))


def format_duration(seconds: float) -> str:
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    minutes, sec = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m{sec:02d}s"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h{minutes:02d}m"


def load_config() -> dict:
    try:
        return json.loads(CFG.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"❌ config.json not found: {CFG}")
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"❌ config.json parse error: {exc}")
        sys.exit(1)


def validate_config(cfg: dict) -> list[str]:
    errors: list[str] = []
    for root_key in ("bbox_wgs84", "zoom", "tiles"):
        if root_key not in cfg:
            errors.append(f"{root_key} is required")

    if errors:
        return errors

    bbox = cfg["bbox_wgs84"]
    zoom = cfg["zoom"]
    tiles = cfg["tiles"]

    if bbox["west"] >= bbox["east"]:
        errors.append("bbox_wgs84: west must be less than east")
    if bbox["south"] >= bbox["north"]:
        errors.append("bbox_wgs84: south must be less than north")

    zmin = zoom["min"]
    zmax = zoom["max"]
    zdef = zoom.get("default", zmin)
    if zmin > zmax:
        errors.append("zoom.min must be <= zoom.max")
    if not (zmin <= zdef <= zmax):
        errors.append("zoom.default must be between min and max")
    if zmin < 0 or zmax > 20:
        errors.append("zoom range should be between 0 and 20")

    local = tiles.get("local_template", "")
    if ".." in local or local.startswith("/"):
        errors.append("tiles.local_template must be safe relative path")
    if any(p not in local for p in ("{z}", "{x}", "{y}")):
        errors.append("tiles.local_template must contain {z}/{x}/{y}")
    if any(p not in tiles.get("source_template", "") for p in ("{z}", "{x}", "{y}")):
        errors.append("tiles.source_template must contain {z}/{x}/{y}")

    policy = cfg.get("offline_collection_policy", {})
    nz = policy.get("nationwide_until_zoom")
    if nz is not None and not (zmin <= nz <= zmax):
        errors.append("offline_collection_policy.nationwide_until_zoom must be within zoom range")

    return errors


def normalize_tile_range(bbox: dict, z: int) -> tuple[int, int, int, int]:
    x0 = lon2tilex(bbox["west"], z)
    x1 = lon2tilex(bbox["east"], z)
    y0 = lat2tiley(bbox["north"], z)
    y1 = lat2tiley(bbox["south"], z)
    if x1 < x0:
        x0, x1 = x1, x0
    if y1 < y0:
        y0, y1 = y1, y0
    return x0, x1, y0, y1


def estimate_tile_count_for_bbox(bbox: dict, zmin: int, zmax: int) -> int:
    total = 0
    for z in range(zmin, zmax + 1):
        x0, x1, y0, y1 = normalize_tile_range(bbox, z)
        total += (x1 - x0 + 1) * (y1 - y0 + 1)
    return total


def bbox_for_zoom(cfg: dict, z: int, scope_mode: str) -> tuple[dict, str]:
    if scope_mode == "nagoya":
        return cfg["bbox_wgs84"], "nagoya"
    if scope_mode == "nationwide":
        jp = cfg.get("bbox_japan_wgs84", cfg["bbox_wgs84"])
        return jp, "nationwide"

    # mixed
    policy = cfg.get("offline_collection_policy", {})
    nz = policy.get("nationwide_until_zoom")
    jp = cfg.get("bbox_japan_wgs84")
    if isinstance(nz, int) and jp and z <= nz:
        return jp, "nationwide"
    return cfg["bbox_wgs84"], "nagoya"


def estimate_collection(cfg: dict, zmin: int, zmax: int, scope_mode: str) -> tuple[int, dict[int, tuple[str, int]]]:
    by_zoom: dict[int, tuple[str, int]] = {}
    total = 0
    for z in range(zmin, zmax + 1):
        bbox, scope = bbox_for_zoom(cfg, z, scope_mode)
        x0, x1, y0, y1 = normalize_tile_range(bbox, z)
        c = (x1 - x0 + 1) * (y1 - y0 + 1)
        by_zoom[z] = (scope, c)
        total += c
    return total, by_zoom


def download(url: str, out_path: Path, timeout: int = 30, retry: int = 0) -> str:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        return "skip"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "OfflineNagoyaMap/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = response.read()
        out_path.write_bytes(data)
        return "ok"
    except Exception as exc:  # noqa: BLE001
        if retry < RETRY_MAX:
            time.sleep(RETRY_DELAY)
            return download(url, out_path, timeout=timeout, retry=retry + 1)
        print(f"  [ERROR] Failed after {RETRY_MAX} retries: {url}")
        print(f"          {type(exc).__name__}: {exc}")
        return "fail"


def clamp_zoom(value: int | None, fallback: int) -> int:
    return fallback if value is None else value


def main() -> None:
    parser = argparse.ArgumentParser(description="Download GSI tiles for offline map")
    parser.add_argument("--sleep", type=float, default=0.05, help="Sleep seconds per request")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt")
    parser.add_argument("--dry-run", action="store_true", help="Only estimate and print plan")
    parser.add_argument("--zmin", type=int, help="Override min zoom for this execution")
    parser.add_argument("--zmax", type=int, help="Override max zoom for this execution")
    parser.add_argument("--scope", choices=["mixed", "nagoya", "nationwide"], default="mixed", help="Collection scope mode")
    args = parser.parse_args()

    print("=" * 60)
    print("GSI Tile Downloader - Enhanced Version")
    print("=" * 60)
    print()

    cfg = load_config()
    errors = validate_config(cfg)
    if errors:
        print("❌ Configuration errors:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)

    print("✓ Configuration validated")

    base_zmin = cfg["zoom"]["min"]
    base_zmax = cfg["zoom"]["max"]
    zmin = clamp_zoom(args.zmin, base_zmin)
    zmax = clamp_zoom(args.zmax, base_zmax)
    if zmin > zmax:
        print("❌ --zmin must be <= --zmax")
        sys.exit(1)

    src_tpl = cfg["tiles"]["source_template"]
    local_tpl = cfg["tiles"]["local_template"]

    estimated, by_zoom = estimate_collection(cfg, zmin, zmax, args.scope)
    nagoya_only = estimate_tile_count_for_bbox(cfg["bbox_wgs84"], zmin, zmax)

    print("\nCollection policy:")
    print(f"  Scope mode: {args.scope}")
    print(f"  Nagoya bbox: {cfg['bbox_wgs84']}")
    if "bbox_japan_wgs84" in cfg:
        print(f"  Nationwide bbox: {cfg['bbox_japan_wgs84']}")
    if "offline_collection_policy" in cfg:
        nz = cfg["offline_collection_policy"].get("nationwide_until_zoom")
        print(f"  Policy nationwide_until_zoom: {nz}")
    print(f"  Zoom: {zmin} - {zmax}")
    print(f"  Source: {src_tpl}")
    print(f"\nEstimated tiles (current mode): {estimated:,}")
    print(f"Estimated tiles (Nagoya only): {nagoya_only:,}")
    print("By zoom:")
    for z in range(zmin, zmax + 1):
        scope, c = by_zoom[z]
        print(f"  z{z}: {scope} {c:,} tiles")

    if args.dry_run:
        print("\nDry run complete.")
        sys.exit(0)

    if estimated > 50000 and not args.yes:
        answer = input("⚠ Large tile count. Continue? (y/N): ").strip().lower()
        if answer != "y":
            print("Canceled by user")
            sys.exit(0)

    print("\nStarting download...\n")

    total = ok = skipped = failed = 0
    all_start = time.time()

    for z in range(zmin, zmax + 1):
        bbox, scope = bbox_for_zoom(cfg, z, args.scope)
        x0, x1, y0, y1 = normalize_tile_range(bbox, z)

        z_total = (x1 - x0 + 1) * (y1 - y0 + 1)
        z_count = 0
        z_start = time.time()
        print(f"[Zoom {z} / {scope}] Tiles: {z_total:,} ({x0}-{x1} x {y0}-{y1})")

        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                url = src_tpl.replace("{z}", str(z)).replace("{x}", str(x)).replace("{y}", str(y))
                out_rel = local_tpl.replace("{z}", str(z)).replace("{x}", str(x)).replace("{y}", str(y))
                out_path = HERE / out_rel

                result = download(url, out_path)
                total += 1
                z_count += 1

                if result == "ok":
                    ok += 1
                elif result == "skip":
                    skipped += 1
                else:
                    failed += 1

                time.sleep(args.sleep)

                if z_count % 100 == 0 or z_count == z_total:
                    elapsed = time.time() - z_start
                    rate = z_count / elapsed if elapsed > 0 else 0
                    remaining = z_total - z_count
                    eta = remaining / rate if rate > 0 else 0
                    progress = (z_count * 100) // z_total
                    print(
                        f"  Progress: {z_count}/{z_total} ({progress}%)"
                        f" | Rate: {rate:.1f} tiles/s | ETA: {format_duration(eta)}",
                        end="\r" if z_count != z_total else "\n",
                    )

        z_elapsed = time.time() - z_start
        print(f"  Completed: ok={ok} skip={skipped} fail={failed} | Time: {format_duration(z_elapsed)}")
        print()

    total_elapsed = time.time() - all_start

    print("=" * 60)
    print("Download Complete")
    print("=" * 60)
    print(f"Total tiles processed: {total:,}")
    print(f"  Downloaded: {ok:,}")
    print(f"  Skipped (already exist): {skipped:,}")
    print(f"  Failed: {failed:,}")
    print(f"Total time: {format_duration(total_elapsed)}")

    if failed:
        print("\n⚠ Some tiles failed. Re-run to retry failed/missing tiles.")
        sys.exit(2)

    print("\n✓ All tiles downloaded successfully!")
    print("\nNext step: Open app/index.html in your browser to view the offline map.")


if __name__ == "__main__":
    main()
