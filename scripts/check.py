"""Check every manifest, and that index.json matches the folders.

Run it with no arguments and it reads files only, which is what CI does. Pass --fetch to
download every file and check its size and hash, which takes a long while and is off by
default. --only narrows that download to a few ids.
"""

import argparse
import hashlib
import json
import re
import sys
import tempfile
import urllib.request
from pathlib import Path

import build_index

KINDS = {"runtime", "model"}
TASKS = {"synthesis", "depth", "matte", "segmentation"}
PLATFORMS = {"windows-x86_64", "macos-aarch64", "macos-x86_64", "linux-x86_64", "any"}
UNPACKS = {"file", "zip"}

# The one task each family does. The engine refuses a pack whose task and arch
# disagree, so the catalogue refuses it first.
ARCH_TASK = {
    "rife": "synthesis",
    "depth-anything": "depth",
    "rvm": "matte",
    "birefnet": "matte",
    "sam2": "segmentation",
}
ARCHS = set(ARCH_TASK)

DEPTH_KINDS = {"inverse-relative", "metric"}

TOP_KEYS = {
    "format", "id", "kind", "name", "version", "summary", "notes", "licence",
    "licence_url", "homepage", "size", "requires", "platforms", "model",
}
TOP_REQUIRED = [
    "format", "id", "kind", "name", "version", "summary", "licence", "size",
    "requires", "platforms",
]
DOWNLOAD_KEYS = {"url", "sha256", "size", "unpack", "dest", "entries"}

ID = re.compile(r"^[a-z0-9-]+$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
FILENAME = re.compile(r"^[A-Za-z0-9._-]+$")

CHUNK = 1 << 20


class Problems:
    """Everything wrong, collected so one run tells you all of it."""

    def __init__(self):
        self.lines = []

    def say(self, where, what):
        self.lines.append(f"{where}: {what}")

    def want(self, where, ok, what):
        if not ok:
            self.say(where, what)
        return ok


def text(value):
    return isinstance(value, str) and value.strip() != ""


def count(value):
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def names(how_many):
    """A list of exactly this many tensor names."""
    def shaped(value):
        return (isinstance(value, list) and len(value) == how_many
                and all(text(x) for x in value))
    return shaped


def triple(value):
    """Three numbers, one per colour channel."""
    return (isinstance(value, list) and len(value) == 3
            and all(isinstance(x, (int, float)) and not isinstance(x, bool)
                    for x in value))


# Every key each architecture's struct in crates/lumit-ml/src/manifest.rs
# declares, and the shape its value takes. The engine's own reader drops a key
# it has no field for without a word, so it cannot report a catalogue that has
# drifted away from it and this table is the only thing that can.
MODEL_KEYS = {
    "rife": {
        "file": text, "img0": text, "img1": text, "timestep": text,
        "output": text, "multiple": count,
    },
    "depth-anything": {
        "file": text, "input": text, "output": text, "size": count,
        "multiple": count, "mean": triple, "std": triple, "output_kind": text,
    },
    "rvm": {
        "file": text, "src": text, "state_in": names(4), "state_out": names(4),
        "downsample": text, "foreground": text, "matte": text,
    },
    "birefnet": {
        "file": text, "input": text, "output": text, "size": count,
        "mean": triple, "std": triple,
    },
    "sam2": {
        "encoder": text, "decoder": text, "image": text, "embed": text,
        "high_res": names(2), "point_coords": text, "point_labels": text,
        "mask_input": text, "has_mask_input": text, "masks": text,
        "iou": text, "size": count, "mean": triple, "std": triple,
    },
}


def check_download(d, where, p):
    """One file the app fetches, and where it lands in the addon folder."""
    dests = []
    if not isinstance(d, dict):
        p.say(where, "a download is not an object")
        return dests
    unknown = sorted(set(d) - DOWNLOAD_KEYS)
    p.want(where, not unknown, f"unknown keys in a download: {', '.join(unknown)}")
    p.want(where, text(d.get("url")) and d["url"].startswith("https://"),
           "a download has no https url")
    p.want(where, SHA256.match(str(d.get("sha256", ""))) is not None,
           "sha256 is not 64 lowercase hex characters")
    p.want(where, count(d.get("size")), "a download has no size in bytes")

    unpack = d.get("unpack")
    if not p.want(where, unpack in UNPACKS, f"unpack is {unpack!r}, not file or zip"):
        return dests

    if unpack == "file":
        dest = d.get("dest")
        if p.want(where, text(dest) and FILENAME.match(dest) is not None,
                  "unpack file needs a plain dest filename"):
            dests.append(dest)
        p.want(where, "entries" not in d, "unpack file must not carry entries")
    else:
        entries = d.get("entries")
        if not p.want(where, isinstance(entries, dict) and entries,
                      "unpack zip needs entries"):
            return dests
        p.want(where, "dest" not in d, "unpack zip must not carry dest")
        for inside, dest in entries.items():
            if p.want(where, text(inside) and text(dest) and FILENAME.match(dest),
                      f"entry {inside!r} has no plain dest filename"):
                dests.append(dest)
    return dests


def check_model(model, where, dests, p):
    """The task, the family, every tensor key, and the files they live in."""
    if not p.want(where, isinstance(model, dict), "model is not an object"):
        return
    task = model.get("task")
    p.want(where, task in TASKS, f"task is {task!r}, not one of the four")
    arch = model.get("arch")
    if not p.want(where, arch in ARCHS,
                  f"arch is {arch!r}, which the engine has no code for"):
        return
    p.want(where, task == ARCH_TASK[arch],
           f"this pack says it does {task!r} and {arch} does {ARCH_TASK[arch]!r}")

    wanted = MODEL_KEYS[arch]
    unknown = sorted(set(model) - set(wanted) - {"task", "arch"})
    p.want(where, not unknown,
           f"keys a {arch} block has no field for: {', '.join(unknown)}")
    for key, shaped in wanted.items():
        if key in model:
            p.want(where, shaped(model[key]),
                   f"{key} is {model[key]!r}, which is not what {arch} takes")
    if text(model.get("output_kind")):
        p.want(where, model["output_kind"] in DEPTH_KINDS,
               f"output_kind is {model['output_kind']!r}, not "
               f"{' or '.join(sorted(DEPTH_KINDS))}")

    files = [model[key] for key in ("file", "encoder", "decoder")
             if text(model.get(key))]
    if not p.want(where, files, "the model names no file"):
        return
    for name in files:
        p.want(where, name in dests,
               f"the model names {name!r}, which no download writes")


def check_manifest(m, ids, p):
    """One addon.json against the rules in the addons note."""
    where = f"addons/{m.get('id', '?')}/addon.json"
    if not isinstance(m, dict):
        p.say(where, "the manifest is not an object")
        return

    unknown = sorted(set(m) - TOP_KEYS)
    p.want(where, not unknown, f"unknown keys: {', '.join(unknown)}")
    missing = [k for k in TOP_REQUIRED if k not in m]
    if not p.want(where, not missing, f"missing keys: {', '.join(missing)}"):
        return

    p.want(where, m["format"] == 1, f"format is {m['format']!r}, not 1")
    p.want(where, text(m["id"]) and ID.match(m["id"]) and len(m["id"]) <= 64,
           "id must be lowercase letters, digits and hyphens, 64 at most")
    p.want(where, m["kind"] in KINDS, f"kind is {m['kind']!r}, not runtime or model")
    for key in ("name", "version", "summary", "licence"):
        p.want(where, text(m[key]), f"{key} is empty")
    for key in ("notes", "licence_url", "homepage"):
        if key in m:
            p.want(where, text(m[key]), f"{key} is empty")
    p.want(where, count(m["size"]), "size is not a count of bytes")

    requires = m["requires"]
    if p.want(where, isinstance(requires, list), "requires is not a list"):
        for need in requires:
            p.want(where, need in ids, f"requires {need!r}, which is not in the catalogue")
            p.want(where, need != m["id"], "requires itself")

    platforms = m["platforms"]
    dests = []
    if p.want(where, isinstance(platforms, dict) and platforms, "platforms is empty"):
        for key, block in platforms.items():
            p.want(where, key in PLATFORMS, f"{key!r} is not a platform key")
            downloads = block.get("downloads") if isinstance(block, dict) else None
            if p.want(where, isinstance(downloads, list) and downloads,
                      f"{key} has no downloads"):
                for d in downloads:
                    dests += check_download(d, where, p)

    if m["kind"] == "runtime":
        p.want(where, "model" not in m, "the runtime carries no model block")
        p.want(where, requires == [], "the runtime requires nothing")
    else:
        if p.want(where, "model" in m, "a model pack needs a model block"):
            check_model(m["model"], where, dests, p)


def check_index(p):
    """index.json is built from the folders, never edited by hand."""
    wanted = build_index.dump(build_index.build())
    if not build_index.INDEX.is_file():
        p.say("index.json", "missing, run scripts/build_index.py")
        return
    if build_index.INDEX.read_text(encoding="utf-8") != wanted:
        p.say("index.json", "does not match the folders, run scripts/build_index.py")


def fetch(url, size, sha256):
    """Pull the file down and hand back what is wrong with it, if anything."""
    digest = hashlib.sha256()
    got = 0
    request = urllib.request.Request(url, headers={"User-Agent": "lumit-addons-check"})
    with urllib.request.urlopen(request) as response, tempfile.TemporaryFile() as tmp:
        while True:
            chunk = response.read(CHUNK)
            if not chunk:
                break
            tmp.write(chunk)
            digest.update(chunk)
            got += len(chunk)
    if got != size:
        return f"is {got} bytes, the manifest says {size}"
    if digest.hexdigest() != sha256:
        return f"hashes to {digest.hexdigest()}, the manifest says {sha256}"
    return None


def check_files(manifests, only, p):
    for m in manifests:
        if only and m.get("id") not in only:
            continue
        where = f"addons/{m.get('id', '?')}/addon.json"
        for block in m.get("platforms", {}).values():
            for d in block.get("downloads", []):
                print(f"  fetching {d['url']}")
                try:
                    wrong = fetch(d["url"], d["size"], d["sha256"])
                except OSError as e:
                    wrong = f"would not download ({e})"
                if wrong:
                    p.say(where, f"{d['url']} {wrong}")


def main():
    parser = argparse.ArgumentParser(description="Check the addon catalogue")
    parser.add_argument("--fetch", action="store_true",
                        help="download every file and check its size and hash")
    parser.add_argument("--only", default="",
                        help="comma separated addon ids to fetch, when --fetch is on")
    args = parser.parse_args()

    p = Problems()
    folders = sorted(x for x in build_index.ADDONS.iterdir() if x.is_dir())
    manifests = []
    for folder in folders:
        path = folder / "addon.json"
        if not path.is_file():
            p.say(f"addons/{folder.name}", "no addon.json")
            continue
        try:
            with path.open(encoding="utf-8") as f:
                m = json.load(f)
        except json.JSONDecodeError as e:
            p.say(f"addons/{folder.name}/addon.json", f"will not parse ({e})")
            continue
        if m.get("id") != folder.name:
            p.say(f"addons/{folder.name}/addon.json",
                  f"id is {m.get('id')!r}, the folder is {folder.name!r}")
        manifests.append(m)

    ids = {m.get("id") for m in manifests}
    for m in manifests:
        check_manifest(m, ids, p)
    check_index(p)

    if args.fetch:
        only = {x for x in args.only.split(",") if x}
        unknown = sorted(only - ids)
        if unknown:
            p.say("--only", f"no such addon: {', '.join(unknown)}")
        else:
            check_files(manifests, only, p)

    for line in p.lines:
        print(line)
    if p.lines:
        print(f"\n{len(p.lines)} problems in {len(manifests)} addons")
        return 1
    print(f"{len(manifests)} addons, all good")
    return 0


if __name__ == "__main__":
    sys.exit(main())
