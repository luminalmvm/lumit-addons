# SAM 2.1 Hiera Tiny

With the Roto brush's seed row set to Segment, a tap on the base frame goes to this and
the matte it traces becomes the seeds the brush propagates from. It replaces nothing:
the strokes still go on top.

The zip is `sam2.1_hiera_tiny_20260221.zip` from the
`vietanhdev/segment-anything-2.1-onnx-models` model page, an export of Meta's SAM 2.1
under Apache-2.0. The encoder runs once a frame and the decoder runs once a point.

| Tensor | Shape | Notes |
| --- | --- | --- |
| `image` | [1, 3, 1024, 1024] | encoder in, ImageNet mean and std |
| `image_embed`, `high_res_feats_0`, `high_res_feats_1` | [1, 256, 64, 64], [1, 32, 256, 256], [1, 64, 128, 128] | encoder out, the decoder wants all three |
| `point_coords`, `point_labels` | [1, N, 2], [1, N] | the taps, 1 for keep and 0 for drop |
| `mask_input`, `has_mask_input` | [1, 1, 256, 256], [1] | a matte from a previous run, zeros if there is none |
| `masks`, `iou_predictions` | [1, 3, 256, 256], [1, 3] | logits, take the one scored highest |
