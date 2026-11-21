# Depth Anything V3 Small

The Depth effect uses this to guess how far away every pixel is. The result is a depth
map a Depth of field, a Set matte or a track matte on another layer can read. It
replaces Depth Anything V2 Small, and it runs first when both are installed.

The files are the ONNX export from the `onnx-community/depth-anything-v3-small` model
page, pinned to one revision. Depth Anything 3 Small carries its own Apache-2.0 licence
and is trained on public academic datasets. The larger Depth Anything 3 models are not
listed: Giant and Large are CC BY-NC.

The weights sit in two files. `model.onnx` is the graph and `model.onnx_data` holds the
numbers, and the graph finds them by that name, so both stay together in the folder.

| Tensor | Shape | Notes |
| --- | --- | --- |
| `pixel_values` | [1, 1, 3, h, w] | ImageNet mean and std, h and w multiples of 14, 504 on the long side |
| `predicted_depth` | [1, 1, h, w] | a distance, bigger is further, relative to this frame only |

Lumit reads the plane as one over the distance, so nearer is larger, the same as V2.
The model's other outputs (confidence, camera pose) are not used.

`supersedes` is not part of the manifest Lumit reads. It tells the Addons page to leave
the named pack out of the list for builds that can take this one. Older builds cannot
read this pack and keep offering the V2 pack.
