# RIFE 4.9

Retime's Flow engine can hand its in-between frames to this instead of the built-in
optical flow. It looks at the two real frames around the one being asked for and paints
the frame between them.

The file is the ensemble export of RIFE 4.9 from the `yuvraj108c/rife-onnx` model page,
which is Practical-RIFE's own release under MIT.

| Tensor | Shape | Notes |
| --- | --- | --- |
| `img0` | [1, 3, H, W] | RGB 0 to 1, H and W padded to a multiple of 32 |
| `img1` | [1, 3, H, W] | the frame after |
| `timestep` | [1] | where between the two, 0 to 1 |
| `output` | [1, 3, H, W] | RGB 0 to 1, cropped back to the real size |
