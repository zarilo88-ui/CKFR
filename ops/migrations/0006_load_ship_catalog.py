import re

from django.db import migrations


def _parse_crew(value: str) -> tuple[int, int]:
    value = (value or "").strip()
    if not value or value in {"-", "?"}:
        return 0, 0

    cleaned = re.sub(r"\s+", "", value)
    if "-" in cleaned:
        start, end = cleaned.split("-", 1)
        try:
            minimum = int(start)
        except ValueError:
            minimum = 0
        try:
            maximum = int(end)
        except ValueError:
            maximum = minimum
    else:
        try:
            minimum = maximum = int(cleaned)
        except ValueError:
            minimum = maximum = 0

    if maximum < minimum:
        maximum = minimum

    return minimum, maximum


def _determine_category(role: str) -> str:
    text = (role or "").lower()

    capital_keywords = [
        "destroyer",
        "frigate",
        "corvette",
        "carrier",
        "dread",
        "capital",
        "large passenger",
        "heavy gunship",
        "heavy freight",
        "heavy salvage",
        "heavy construction",
        "heavy mining",
        "light carrier",
    ]
    if any(keyword in text for keyword in capital_keywords):
        return "CAP"

    if "heavy fighter" in text:
        return "HF"
    if "medium fighter" in text:
        return "MF"
    if "light fighter" in text or "snub" in text or "racing" in text:
        return "LF"

    if "gunship" in text:
        return "HF"
    if "bomber" in text:
        return "MF"

    support_keywords = [
        "freight",
        "cargo",
        "transport",
        "expedition",
        "exploration",
        "dropship",
        "medical",
        "passenger",
        "science",
        "refuel",
        "repair",
        "salvage",
        "mining",
        "pathfinder",
        "data",
        "boarding",
        "interdiction",
        "modular",
        "rescue",
    ]
    if any(keyword in text for keyword in support_keywords):
        return "MR"

    return "MR"


def load_ship_catalog(apps, schema_editor):
    Ship = apps.get_model("ops", "Ship")

    from ops.data.ships_catalog import SHIPS_DATA

    for entry in SHIPS_DATA:
        min_crew, max_crew = _parse_crew(entry.get("crew", ""))
        category = _determine_category(entry.get("role", ""))
        cargo = entry.get("cargo", "-").strip() or "-"

        ship, _ = Ship.objects.update_or_create(
            name=entry["name"],
            defaults={
                "manufacturer": entry.get("manufacturer", ""),
                "role": entry.get("role", ""),
                "cargo_capacity": cargo,
                "min_crew": min_crew or 0,
                "max_crew": max(min_crew or 0, max_crew or 0),
                "category": category,
            },
        )

        # Ensure max crew is at least min crew
        if ship.max_crew < ship.min_crew:
            ship.max_crew = ship.min_crew
            ship.save(update_fields=["max_crew"])


class Migration(migrations.Migration):

    dependencies = [
        ("ops", "0005_ship_cargo_capacity_ship_manufacturer_ship_role_and_more"),
    ]

    operations = [
        migrations.RunPython(load_ship_catalog, migrations.RunPython.noop),
    ]