# Model runtime

Every model pack needs this one and nothing runs without it. It is ONNX Runtime 1.24.4,
with DirectML on Windows and CoreML on macOS.

Windows takes `onnxruntime.dll` and `onnxruntime_providers_shared.dll` from the NuGet
package `Microsoft.ML.OnnxRuntime.DirectML`, and `DirectML.dll` from
`Microsoft.AI.DirectML` 1.15.4. Linux takes the library from the CPU package
`Microsoft.ML.OnnxRuntime`. macOS takes the same library out of that package, signed again
with Lumit's Developer ID and kept on this repository's releases, since Lumit only loads
libraries signed by its own team.

ONNX Runtime is MIT. DirectML carries its own Microsoft licence, which allows
redistribution inside an application built with a machine learning framework, and both
licence files are installed beside the libraries.

Intel Macs get no block here, since ONNX Runtime stopped shipping an `osx-x64` build
after 1.23.

Windows pulls 205 MB of NuGet package down for 36 MB of library, because that is where
Microsoft publishes them. Trimming that into a zip on this repository's releases is a
later step.

| Platform | Files installed |
| --- | --- |
| windows-x86_64 | onnxruntime.dll, onnxruntime_providers_shared.dll, DirectML.dll, LICENSE-onnxruntime.txt, LICENSE-directml.txt |
| macos-aarch64 | libonnxruntime.dylib, LICENSE-onnxruntime.txt |
| linux-x86_64 | libonnxruntime.so, LICENSE-onnxruntime.txt |
