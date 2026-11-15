# Robust Video Matting ResNet50

Remove background uses this to cut a person out of their background. It carries its own
state from one frame to the next, so a run starts at the first frame and a cancel keeps
what it reached.

The file is `rvm_resnet50_fp32.onnx` from the Robust Video Matting v1.0.0 release,
under GPL-3.0. It is the ResNet50 version of the same model, about 107 MB against 15 MB,
with the same tensors. It is the larger of the two and the one that runs if both are
installed. Its id starts with `matting` so that it is listed ahead of `rvm`.

`downsample_ratio` comes from the model's own table, picked by the long side of the
frame and by the detail row: 512 takes 1, 1280 takes 0.375 for a portrait and 0.6 for a
full body, 1920 takes 0.25 and 0.4, 3840 takes 0.125 and 0.2.

| Tensor | Shape | Notes |
| --- | --- | --- |
| `src` | [1, 3, H, W] | RGB 0 to 1 |
| `r1i` to `r4i` | recurrent state | zeros [1, 1, 1, 1] on the first frame, then the last `r1o` to `r4o` |
| `downsample_ratio` | [1] | from the table above |
| `fgr`, `pha` | [1, 1, H, W] | foreground and coverage |
