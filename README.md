# Zig for OpenHarmony

English | [简体中文](README.zh-CN.md)

Zig **0.17.0** with OpenHarmony (OHOS) support. This repository provides a
[complete source patch](patch/zig-ohos-0.17.x.patch), host compilers for cross
development, and native compilers for three OHOS architectures. The patch is
based on the official Zig 0.17.0 release.

The toolchain includes OHOS libc, headers, C/C++ runtime support, and IEEE
binary128 `long double` support for OHOS x86_64. Each host compiler can target
all three OHOS architectures below.

## Downloads

Download packages from [GitHub Releases](https://github.com/openharmony-zig/zig-patch/releases).
Choose a **host** package for cross compilation, or a **native** package to run
Zig on OHOS itself.

| Kind | Platform | Target | CPU | Archive formats |
| --- | --- | --- | --- | --- |
| Host | macOS ARM64 | `aarch64-macos-none` | `baseline` | `.tar.xz`, `.tar.gz` |
| Host | Linux x86_64 GNU | `x86_64-linux-gnu` | `baseline` | `.tar.xz`, `.tar.gz` |
| Host | Linux x86_64 musl | `x86_64-linux-musl` | `baseline` | `.tar.xz`, `.tar.gz` |
| Host | Windows x86_64 GNU | `x86_64-windows-gnu` | `baseline` | `.tar.xz`, `.tar.gz` |
| Native | OHOS ARM64 | `aarch64-linux-ohos` | `baseline` | `.tar.xz` |
| Native | OHOS ARMv7 | `arm-linux-ohoseabi` | `generic+v7a` | `.tar.xz` |
| Native | OHOS x86_64 | `x86_64-linux-ohos` | `baseline` | `.tar.xz` |

Archive names follow `zig-<target>-<cpu>.tar.xz` or `.tar.gz`. Each xz archive
has a `.tar.xz.sha256` companion. The 0.17.0 asset set follows the same names
and formats as [0.16.0](https://github.com/openharmony-zig/zig-patch/releases/tag/0.16.0):
seven xz archives, seven checksum files, and four host gzip archives, for
**18 uploaded assets**. GitHub generates the two source archives from the
release tag.

## Quick start

For example, download the macOS ARM64 xz archive and its checksum, then run:

```sh
shasum -a 256 -c zig-aarch64-macos-none-baseline.tar.xz.sha256
tar -xf zig-aarch64-macos-none-baseline.tar.xz
./zig-aarch64-macos-none-baseline/zig version
```

The expected version is `0.17.0`. On Linux, `sha256sum -c <checksum-file>` can
verify the checksum. Windows packages use `zig.exe`. Keep the extracted
`lib/` directory alongside the compiler.

With the extracted host package on `PATH`, compile your Zig, C, or C++ sources:

```sh
zig build-exe main.zig -target aarch64-linux-ohos -lc -O ReleaseFast
zig cc main.c -target aarch64-linux-ohos -o hello-ohos
zig c++ main.cpp -target aarch64-linux-ohos -o hello-cxx-ohos
```

Use `arm-linux-ohoseabi -mcpu=generic+v7a` for ARMv7 or
`x86_64-linux-ohos` for x86_64. Run the resulting programs on the matching
OHOS device or system image.

## Build and contribute

See the [development guide](docs/develop.md) for a fresh checkout build,
patch maintenance, release packaging, and QEMU tests.

Validation uses the pinned OHOS QEMU images and SDK **6.1.1.125 / API 24**.
The [validation scope](docs/develop.md#validation-scope) describes the host and
native compiler checks, dependency reuse, and observed limitations.

## License

Original additions in this repository use [MIT](LICENSE), with the same license
text and `2025-present richerfu` copyright notice as
[zig-napi](https://github.com/openharmony-zig/zig-napi/blob/main/LICENSE).
Zig's original MIT license and contributor notice are preserved verbatim in
[LICENSE-ZIG](LICENSE-ZIG). Bundled upstream code retains its own licenses;
see [third-party notices](THIRD_PARTY_NOTICES.md#english).
