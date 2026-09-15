# Depth Anything V2 Small

The Depth effect uses this to guess how far away every pixel is. The result is a depth
map a Depth of field, a Set matte or a track matte on another layer can read.

The file is the ONNX export from the `onnx-community/depth-anything-v2-small` model
page, which carries Depth Anything V2 Small's own Apache-2.0 licence.

| Tensor | Shape | Notes |
| --- | --- | --- |
| `pixel_values` | [1, 3, h, w] | ImageNet mean and std, h and w multiples of 14, 518 on the long side |
| `predicted_depth` | [1, h, w] | bigger is nearer, relative to this frame only |
