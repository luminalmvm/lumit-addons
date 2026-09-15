"""Write index.json from the addon folders.

The catalogue is nothing but the manifests. Every addons/<id>/addon.json goes into the
list whole, so installing an addon is a copy of its entry into the folder.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ADDONS = ROOT / "addons"
INDEX = ROOT / "index.json"


def manifests(addons=ADDONS):
    """Every manifest, in folder order, so two runs give the same file."""
    found = []
    for folder in sorted(p for p in addons.iterdir() if p.is_dir()):
        path = folder / "addon.json"
        if not path.is_file():
            raise SystemExit(f"{folder.name}: no addon.json")
        with path.open(encoding="utf-8") as f:
            found.append(json.load(f))
    return found


def build(addons=ADDONS):
    return {"format": 1, "addons": manifests(addons)}


def dump(index):
    """The exact text index.json holds, so the check can compare it as a string."""
    return json.dumps(index, indent=2, ensure_ascii=False) + "\n"


def main():
    index = build()
    with open(INDEX, "w", encoding="utf-8", newline="\n") as f:
        f.write(dump(index))
    print(f"index.json: {len(index['addons'])} addons")


if __name__ == "__main__":
    main()
