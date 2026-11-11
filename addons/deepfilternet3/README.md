# DeepFilterNet3

Voice isolation uses this to keep speech and turn everything else down: traffic, wind,
music, a room's hum. It runs on the processor, on your own machine, about 25 times faster
than the sound plays.

The three files are the ONNX export in the `Rikorose/DeepFilterNet` repository, under
MIT or Apache-2.0, fetched as the tarball at a fixed commit. Lumit makes the features
and puts the sound back together itself, so the models only ever see numbers.

- `enc.onnx` reads the sound's bands and fine spectrum and hands both decoders what it
  heard.
- `erb_dec.onnx` gives each of 32 bands a gain.
- `df_dec.onnx` gives the lowest 96 bins a short filter that rebuilds the voice's detail.

| Tensor | Shape | Notes |
| --- | --- | --- |
| `feat_erb` | [1, 1, n, 32] | encoder in, each band's level in dB, normalised as it runs |
| `feat_spec` | [1, 2, n, 96] | encoder in, the lowest 96 bins, real and imaginary, normalised |
| `m` | [1, 1, n, 32] | band decoder out, a gain per band |
| `coefs` | [1, n, 96, 10] | filter decoder out, five complex taps per bin |

The decoders take what the encoder hands back by name. Frames are 20 ms at 48 kHz, a
960-point transform with a 480-sample hop, and the model looks two frames ahead.
