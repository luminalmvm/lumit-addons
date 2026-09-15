# BiRefNet Lite

The other model Remove background offers. It looks at one frame on its own and cuts out
whatever the subject is, so it suits a still or a shot with no person in it.

The file is the ONNX export from the `onnx-community/BiRefNet_lite-ONNX` model page.
BiRefNet's code is MIT, but the weights are trained on DIS5K, whose terms are
non-commercial, and Lumit says so on the row.

| Tensor | Shape | Notes |
| --- | --- | --- |
| `input_image` | [1, 3, 1024, 1024] | ImageNet mean and std |
| `output_image` | [1, 1, 1024, 1024] | logits, sigmoid for coverage |
