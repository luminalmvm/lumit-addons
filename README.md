# Lumit addons

The catalogue of official addons for [Lumit](https://lumitlab.com).

An addon is a large optional download Lumit never ships and never fetches on its own.
One of them is the model runtime, the rest are model packs, and a pack is one model with
its licence and a manifest saying what it does. Lumit works fully without every one of
them.

Every model here is an analysis model and it runs on your own machine, on your own
graphics card. There is no account, no server and nothing metered. A model here produces
a depth map, a matte, an in-between frame, or the shape of the thing you clicked on, and
that is the whole list. Nothing generative will ever be listed: no text to image, no
image to video, no prompt-written shaders, no bring-your-own-key provider.

## How the app reads this

Press Check for addons on the Addons page in Settings and Lumit fetches `index.json`
from this repository's main branch. Nothing is fetched at start-up and nothing is probed
on a timer, so that button is the only time the app looks.

`index.json` is built from the folders under `addons/`. Each folder holds its
`addon.json` manifest and a README naming where the file comes from, its licence, and
the tensors Lumit speaks to it with. An install copies the manifest into the addon
folder unchanged.

Weights are fetched from their upstream release pages today, checked against the SHA-256
in the manifest before Lumit sees them. Re-hosting them on this repository's releases is
a later step, which changes the url and the hash and nothing else.

## Proposing an addon

Open a pull request adding a folder under `addons/`, then run the check.

```
python scripts/build_index.py
python scripts/check.py
```

The first writes `index.json`, which is never edited by hand. The second reads every
manifest and makes sure the index matches the folders, and it runs on every push and
pull request. Pass `--fetch` to download each file and check its size and hash as well,
which takes a while, and `--only <id>` to narrow that to one addon.

What gets in is an analysis model doing one of the four tasks, under a licence anyone
can read. A pack under a non-commercial licence is not listed, and anything generative
is refused.

## Licence

The files in this repository are GPL-3.0, the same as Lumit. Each model keeps its own
licence, named in its manifest and in its README.
