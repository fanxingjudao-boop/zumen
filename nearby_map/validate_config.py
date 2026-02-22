#!/usr/bin/env python3
"""Configuration validator for Nagoya offline map."""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CFG = HERE / "config.json"


def validate_bbox(bbox: dict) -> list[str]:
    errors: list[str] = []
    required = {"west", "east", "south", "north"}
    if not required.issubset(bbox):
        errors.append("bbox_wgs84 must contain west, east, south, north")
        return errors

    west = bbox["west"]
    east = bbox["east"]
    south = bbox["south"]
    north = bbox["north"]

    if west >= east:
        errors.append(f"bbox_wgs84: west ({west}) must be less than east ({east})")
    if south >= north:
        errors.append(f"bbox_wgs84: south ({south}) must be less than north ({north})")
    if not (-180 <= west <= 180):
        errors.append(f"bbox_wgs84: west ({west}) must be between -180 and 180")
    if not (-180 <= east <= 180):
        errors.append(f"bbox_wgs84: east ({east}) must be between -180 and 180")
    if not (-90 <= south <= 90):
        errors.append(f"bbox_wgs84: south ({south}) must be between -90 and 90")
    if not (-90 <= north <= 90):
        errors.append(f"bbox_wgs84: north ({north}) must be between -90 and 90")

    return errors


def validate_zoom(zoom: dict) -> list[str]:
    errors: list[str] = []
    required = {"min", "max", "default"}
    if not required.issubset(zoom):
        errors.append("zoom must contain min, max, default")
        return errors

    zmin = zoom["min"]
    zmax = zoom["max"]
    zdef = zoom["default"]

    if zmin > zmax:
        errors.append(f"zoom: min ({zmin}) must be less than or equal to max ({zmax})")
    if not (zmin <= zdef <= zmax):
        errors.append(f"zoom: default ({zdef}) must be between min ({zmin}) and max ({zmax})")
    if zmin < 0 or zmax > 20:
        errors.append(f"zoom: range ({zmin}-{zmax}) should be between 0 and 20")

    return errors


def validate_center(center: dict) -> list[str]:
    errors: list[str] = []
    required = {"lat", "lon"}
    if not required.issubset(center):
        errors.append("center must contain lat, lon")
        return errors

    lat = center["lat"]
    lon = center["lon"]

    if not (-90 <= lat <= 90):
        errors.append(f"center.lat ({lat}) must be between -90 and 90")
    if not (-180 <= lon <= 180):
        errors.append(f"center.lon ({lon}) must be between -180 and 180")

    return errors


def validate_tiles(tiles: dict) -> list[str]:
    errors: list[str] = []

    if "local_template" not in tiles:
        errors.append("tiles must contain local_template")
        return errors

    local_tpl = tiles["local_template"]

    if ".." in local_tpl:
        errors.append("tiles.local_template must not contain '..'")
    if local_tpl.startswith("/"):
        errors.append("tiles.local_template must not start with '/'")
    if "{z}" not in local_tpl or "{x}" not in local_tpl or "{y}" not in local_tpl:
        errors.append("tiles.local_template must contain {z}, {x}, {y} placeholders")
    if "source_template" not in tiles:
        errors.append("tiles.source_template is required")
    if "attribution" not in tiles or not str(tiles["attribution"]).strip():
        errors.append("tiles.attribution is required (legal requirement for GSI tiles)")
    terms_url = str(tiles.get("terms_url", "")).strip()
    if not terms_url:
        errors.append("tiles.terms_url is required (confirm GSI terms before publish)")
    elif not (terms_url.startswith("https://") or terms_url.startswith("http://")):
        errors.append("tiles.terms_url must be a valid URL")

    return errors


def validate_hazard_layers(layers: list) -> list[str]:
    errors: list[str] = []
    if not isinstance(layers, list):
        return ["hazard_layers must be an array"]
    for idx, layer in enumerate(layers):
        if not isinstance(layer, dict):
            errors.append(f"hazard_layers[{idx}] must be an object")
            continue
        for key in ("id", "name", "template", "source"):
            if not str(layer.get(key, "")).strip():
                errors.append(f"hazard_layers[{idx}].{key} is required")
        tpl = str(layer.get("template", ""))
        if any(ph not in tpl for ph in ("{z}", "{x}", "{y}")):
            errors.append(f"hazard_layers[{idx}].template must contain {{z}}, {{x}}, {{y}}")
    return errors


def main() -> None:
    print("=" * 60)
    print("Configuration Validator")
    print("=" * 60)
    print()

    if not CFG.exists():
        print(f"❌ ERROR: Config file not found: {CFG}")
        sys.exit(1)

    try:
        cfg = json.loads(CFG.read_text(encoding="utf-8"))
        print("✓ Config file loaded successfully")
    except json.JSONDecodeError as exc:
        print(f"❌ ERROR: Invalid JSON format: {exc}")
        sys.exit(1)

    print()

    all_errors: list[str] = []

    for key, validator in (
        ("bbox_wgs84", validate_bbox),
        ("zoom", validate_zoom),
        ("center", validate_center),
        ("tiles", validate_tiles),
    ):
        if key not in cfg:
            all_errors.append(f"{key} is required")
            print(f"❌ {key}: Missing")
            continue

        errors = validator(cfg[key])
        all_errors.extend(errors)
        if errors:
            print(f"❌ {key}: Invalid")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"✓ {key}: Valid")

    if "hazard_layers" in cfg:
        hz_errors = validate_hazard_layers(cfg["hazard_layers"])
        all_errors.extend(hz_errors)
        if hz_errors:
            print("❌ hazard_layers: Invalid")
            for err in hz_errors:
                print(f"  - {err}")
        else:
            print("✓ hazard_layers: Valid")

    print()
    print("=" * 60)

    if all_errors:
        print(f"❌ Validation FAILED: {len(all_errors)} error(s) found")
        sys.exit(1)

    print("✅ Validation PASSED: Configuration is valid")
    print()
    print("You can now run:")
    print("  python download_tiles.py")
    sys.exit(0)


if __name__ == "__main__":
    main()
