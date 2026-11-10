# Whisper Large v3 Turbo

Captions and the Cut transcript use this to write down what was said, word by word,
with when each word was said and who said it. It is the most accurate of the speech
packs and wants a graphics card to be quick.

The pack is three models, and every one runs on your own machine.

- Whisper large-v3-turbo writes the words. The two files are from the
  `onnx-community/whisper-large-v3-turbo_timestamped` model page, an ONNX export of
  OpenAI's Whisper under MIT whose decoder also hands back its cross-attention, which
  is what each word's time is read from. Both are the int8 files. The encoder runs on
  the graphics card where there is one, and the decoder always runs on the processor,
  where it is fastest. `tokenizer.json`, `generation_config.json` and `config.json`
  come from the same page.
- Silero VAD v6.2.1, under MIT, from the `snakers4/silero-vad` repository, hears where
  the speech is. Silence never reaches Whisper.
- 3D-Speaker's ERes2Net, under Apache-2.0, as sherpa-onnx publishes it, tells voices
  apart.

Turbo was trained to transcribe and not to translate, so the pack says it does not
translate and Lumit does not offer to write other languages in English with it.

| Tensor | Shape | Notes |
| --- | --- | --- |
| `input_features` | [1, 128, 3000] | encoder in, log-mel of 30 seconds at 16 kHz |
| `last_hidden_state` | [1, 1500, 1280] | encoder out, the decoder's `encoder_hidden_states` |
| `input_ids` | [1, n] int64 | decoder in, the word pieces so far |
| `use_cache_branch` | [1] bool | false on the first step, true after |
| `past_key_values.{0-3}.{decoder,encoder}.{key,value}` | [1, 20, n, 64] | the cache, fed back from `present.*` |
| `logits` | [1, n, 51866] | the next word piece |
| `cross_attentions.{0-3}` | [1, 20, n, 1500] | heads 2.4, 2.11, 3.3, 3.6, 3.11 and 3.14 time the words |
| `input`, `state`, `sr` | [1, 576], [2, 1, 128], int64 | Silero, 512 new samples and 64 before them |
| `output`, `stateN` | [1, 1], [2, 1, 128] | speech probability, and the state for the next chunk |
| `x` | [1, frames, 80] | ERes2Net, Kaldi filterbank with each band's mean taken away |
| `embedding` | [1, 192] | the voice's fingerprint |
