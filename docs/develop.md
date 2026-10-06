# Development guide

English | [简体中文](develop.zh-CN.md) | [README](../README.md)

This guide covers local source adaptation, builds, packaging, and validation.
Run the commands from the **zig-patch repository root** unless stated otherwise.

## Source baseline and layout

The `zig-bootstrap` submodule is pinned to the official **0.17.0** release
commit on the `0.17.x` branch:

```text
b12ab1fbafc3a290d6a13c42b14e1c67dd826c0f
```

The release date is 2026-10-01. The [official version index](https://ziglang.org/download/index.json)
provides the bootstrap archive and checksum; these are also pinned in
`zig-bootstrap/ohos/manifest.json` after applying the patch.

| Path | Purpose |
| --- | --- |
| `patch/zig-ohos-0.17.x.patch` and `.sha256` | Complete OHOS patch and checksum |
| `scripts/` | Repository entry points and local release preparation |
| `zig-bootstrap/ohos/manifest.json` | Version, source revisions, target/CPU matrix, QEMU image checksums |
| `zig-bootstrap/ohos/source-paths.txt` | Source paths included in patch export |
| `zig-bootstrap/scripts/ohos/` | Build, maintenance, and validation implementations |
| `zig-bootstrap/zig/lib/libc/ohos/` | OHOS libc overlay and OpenLibm binary128 sources |
| `zig-bootstrap/zig/test/ohos/` | Runtime and compiler smoke tests |
| `zig-bootstrap/out/`, `zig-bootstrap/dist/`, `dist/` | Generated builds, packages, and reports |

OHOS-specific submodule paths are created by the patch and are available after
`scripts/apply-ohos-patch.sh`. The patched submodule's `ohos/README.md` also
documents its internal scripts; its examples use the submodule root.

## Build from a fresh checkout

Install Git, a C/C++ compiler, CMake, Ninja, jq, ripgrep, xz, and Python 3.
Use a Unix-like build environment. The complete patch includes the OHOS libc,
headers, OpenLibm sources, and build scripts, so a normal build does not require
an existing build tree or an external OHOS SDK installation. SDK and musl
checkouts are needed when regenerating the overlay.

```sh
git clone --branch 0.17.0 --recurse-submodules https://github.com/openharmony-zig/zig-patch.git
cd zig-patch
scripts/apply-ohos-patch.sh
CMAKE_GENERATOR=Ninja CMAKE_BUILD_PARALLEL_LEVEL=6 scripts/build-matrix.sh
```

The example uses the published `0.17.0` tag. During release preparation, use
the corresponding patch branch instead. For an existing clone, check out the
intended branch or tag and initialize its recorded submodule with
`git submodule update --init --recursive` before applying the patch.
The apply script checks the exact bootstrap base and accepts an already-applied
patch. Each root build/test wrapper also invokes it.

The full matrix builds four host compilers and three native OHOS compilers.
It bootstraps host LLVM/Clang/LLD and Zig, builds the target dependencies, then
builds and installs the target Zig compiler, libraries, and documentation.
Build prefixes are `zig-bootstrap/out/zig-<target>-<cpu>/`; xz packages and
checksum files are written to `zig-bootstrap/dist/`. The archive root matches
the package name. ARMv7 uses `generic+v7a`.

Select groups or individual manifest names:

```sh
scripts/build-matrix.sh --only host
scripts/build-matrix.sh --only native
scripts/build-matrix.sh --only host --targets arm64-macos,x64-linux-musl
scripts/build-matrix.sh --skip-build
scripts/build-matrix.sh --skip-package
```

`--skip-build` validates and packages existing prefixes, including checks for
stale installed OHOS library sources. `--skip-package` builds and checks without
creating archives. The first successful target in a matrix call makes
`zig-bootstrap/out/host` available for reuse by subsequent targets. Separate
calls may set `ZIG_BOOTSTRAP_SKIP_HOST=1` when that host prefix comes from the
same source. Concurrent builds must use different targets and must not share
`out/build-llvm-<target>-<cpu>`.

All OHOS scripts use `zig-bootstrap/out/tmp` for host temporary files by
default. Set `OHOS_TMPDIR` to use another disk.

## Prepare release assets

```sh
python3 scripts/prepare-release.py
```

The script reads packages from `zig-bootstrap/dist/`, checks the bootstrap
base, archive checksums, compiler presence, full manifest, and build metadata,
then prepares the same 18 asset names and formats as 0.16.0:

- Seven `.tar.xz` archives and their seven `.tar.xz.sha256` files.
- Four host `.tar.gz` archives with exactly the same uncompressed tar payloads
  as their xz counterparts.

Upload attachments from `dist/releases/0.17.0/assets/`. The adjacent
`SHA256SUMS` and `release-assets.json` describe all 18 files. GitHub's two
automatically generated source archives come from the published tag.

To prepare the versioned packages retained from the validated local build:

```sh
python3 scripts/prepare-release.py --source-dir zig-bootstrap/dist/0.17.0
```

The script also accepts `--only`, `--targets`, and `--output-dir`. Use a separate
output directory for a different target selection. Build outputs and validation
records are local generated files and are not included in a fresh clone.

## Maintain the patch

Edit the adapted sources in `zig-bootstrap`, then export them:

```sh
scripts/refresh-patch.sh
```

The script uses a temporary Git index to export the paths in
`zig-bootstrap/ohos/source-paths.txt` and refreshes the patch SHA-256 without
changing the submodule's real index. Keep the submodule at the official base;
its applied source changes are carried by the exported patch.

Check source structure, shell syntax, Zig formatting, and all three target
probes with a newly built host compiler:

```sh
zig-bootstrap/scripts/ohos/check-source.sh \
  --zig zig-bootstrap/out/zig-aarch64-macos-none-baseline/zig
```

When changing the Zig baseline, review the adaptation against that release,
update the submodule gitlink, `.gitmodules`, base constants in the apply/export
scripts, manifest and source checks, then regenerate the patch and validate it
on a fresh checkout. The current patch is only guaranteed for the pinned base.

The 0.17.0 adaptation includes `cc_dir` API migration, PIE policy integration,
OHOS DNS table types and ARMv7 fortify compatibility, binary128 `long double`
ABI support, and LLVM hidden sret parameter accounting. Keep the relevant C/Zig
ABI regressions when updating the compiler.

## Regenerate libc and headers

The OHOS libc sources are an overlay against Zig's musl, and OHOS headers are
an overlay derived from the pinned SDK. Check out the musl revision and SDK
version recorded in `zig-bootstrap/ohos/manifest.json`, then compare generated
sources without modifying the checked-out overlay:

```sh
zig-bootstrap/scripts/ohos/update-libc.sh \
  --zig zig-bootstrap/out/zig-aarch64-macos-none-baseline/zig \
  --musl-source /path/to/third_party_musl \
  --sdk-native /path/to/ohos-sdk/native
```

Differences produce a nonzero exit status and are written to
`zig-bootstrap/out/ohos-maintenance/diff/`. Review them before repeating the
command with `--apply` (`rsync` is required). Update generator fixups and compiler
glue as needed, run source and three-architecture runtime checks, then refresh
the patch and update the manifest for an upstream upgrade. The musl license is
included at `zig-bootstrap/zig/lib/libc/musl/COPYRIGHT`.

## Update binary128 OpenLibm

OHOS x86_64 uses IEEE binary128 `long double`. The OpenLibm `v0.8.7` subtree
replaces incompatible x87 long-double sources and is explicitly selected by
`zig-bootstrap/zig/src/libs/ohos.zig`. Its revision and compatibility patch
are pinned in the manifest.

```sh
git clone https://github.com/JuliaMath/openlibm.git /path/to/openlibm
git -C /path/to/openlibm switch --detach 9fbeafcd4f1b6ef6aa3946c1c8faead50f38a94d
zig-bootstrap/scripts/ohos/update-openlibm.sh --source /path/to/openlibm
```

Review `zig-bootstrap/out/ohos-openlibm-maintenance/diff/` before adding
`--apply`. The x86_64 QEMU test exercises `powl`, `expl`, `logl`, and `sqrtl`
and requires the `C_OHOS_F128_OK` marker.

## QEMU validation

Prepare the three image archives from
[harmony-contrib/ohos-qemu](https://github.com/harmony-contrib/ohos-qemu)
at the revision and SHA-256 values pinned in the manifest, plus QEMU and HDC.
The scripts verify the archive checksums and boot complete OpenHarmony
standard-system guests in sequence.

Run the host compiler matrix:

```sh
scripts/test-host-matrix.sh \
  --packages /path/to/ohos-qemu/packages \
  --hdc-endpoint 127.0.0.1:5556
```

This checks each of the four host compilers against all three OHOS architectures
and executes their results in the corresponding guests. It covers static,
static-PIE and dynamic programs, shared libraries/dlopen, malloc extensions,
files, mmap, threads, TLS, atomics, networking/DNS, time, locale, math, and
`zig cc`, `zig c++`, `zig ar`, and `zig ranlib`.

The macOS ARM64 compiler runs natively. Linux compilers run in containers;
on ARM64 hosts, the static musl compiler uses `qemu-x86_64` inside an ARM64
container with two Zig jobs. Windows runs through WineHQ 11 in an x86_64 Linux
environment; ARM64 macOS uses an x86_64 Ubuntu full-system QEMU VM. Docker is
required for these host container checks. Container definitions are in
`zig-bootstrap/ohos/Dockerfile.host-test` and `Dockerfile.host-test-arm64`.

Use `--targets x64-windows-gnu` for one host, `--compile-only` for compilation
and ELF inspection, or `--skip-compile` to rerun QEMU with checked existing
artifacts. The latter two options cannot be combined. VM state and SSH keys
default to `zig-bootstrap/out/ohos-windows-x86-vm/`; use `--windows-vm-dir` and
`--windows-vm-port` to change its location and forwarded SSH port.

Run the three native OHOS compilers:

```sh
scripts/test-qemu.sh \
  --zig zig-bootstrap/out/zig-aarch64-macos-none-baseline/zig \
  --packages /path/to/ohos-qemu/packages \
  --native-zig-root zig-bootstrap/out \
  --native-only \
  --arch all \
  --hdc-endpoint 127.0.0.1:5556
```

Each native compiler runs `version`, `env`, and an in-guest Zig compile/link/run
check requiring `NATIVE_ZIG_OHOS_OK`. `--native-only` uses separate clean boots
for these checks. HDC transfers the compiler directly and a reduced library tar
for the smoke test; release archives always contain the full installed prefix.
Omit `--native-only` to include cross-compiled runtime smoke tests in the same
boot. To check compilation and ELF metadata without guests:

```sh
scripts/test-qemu.sh \
  --zig zig-bootstrap/out/zig-aarch64-macos-none-baseline/zig \
  --compile-only
```

### Windows VM checks

To reproduce the Windows compilation checks independently:

```sh
zig-bootstrap/scripts/ohos/prepare-runtime-kit.sh \
  --zig zig-bootstrap/out/zig-aarch64-macos-none-baseline/zig \
  --output zig-bootstrap/out/ohos-runtime-kit

zig-bootstrap/scripts/ohos/test-windows-vm.sh \
  --zig zig-bootstrap/out/zig-x86_64-windows-gnu-baseline/zig.exe \
  --runtime-kit zig-bootstrap/out/ohos-runtime-kit \
  --work-dir zig-bootstrap/out/windows-host-smoke
```

The control compiler prebuilds a checksummed target runtime kit containing CRT,
libc/libc++, compiler-rt, and std-heavy Zig smoke objects. Windows Zig compiles
C/C++ for all three architectures and an ARM64 Zig probe, runs `ar`/`ranlib`,
and performs the final ELF/DSO links. The kit contains no final executables.
The host matrix prepares this kit automatically. Its isolated Wine runner sets
`ZIG_WINE_FILE_LOCK_WORKAROUND=1` for Wine's incomplete `NtLockFile` support.

### Guest controls and logs

The default HDC endpoint is `127.0.0.1:5555`. Select `127.0.0.1:5556` when
5555 is occupied by DevEco Emulator. Each architecture allows two clean boot
attempts by default; writable images are restored from the verified archive
before each attempt. `--qemu-attempts 1` disables retries.

| Environment variable | Default | Accepted range / purpose |
| --- | --- | --- |
| `QEMU_HDC_COMMAND_TIMEOUT` | 180 seconds | 30–600 seconds for ordinary HDC commands |
| `QEMU_NATIVE_HDC_COMMAND_TIMEOUT` | 600 seconds | 180–1800 seconds for native compiler checks |
| `OHOS_TMPDIR` | `zig-bootstrap/out/tmp` | Host temporary directory |

Build results are in `zig-bootstrap/out/ohos-matrix/build-results.tsv`, host
matrix results in `zig-bootstrap/out/ohos-host-matrix-test/host-results.tsv`,
and standalone QEMU logs in `zig-bootstrap/out/ohos-qemu-test/`.

## Validation scope

The 0.17.0 local validation completed:

- Clean patch replay on the official base, with 1,441 adapted files matching.
- Seven Zig compiler/library/documentation rebuilds from fresh sources and
  empty Zig caches; all compiler binaries and each package's 20,882 library
  files matched the runtime-validated products byte for byte.
- Seven xz packages and 18 release assets, including metadata, checksums, and
  matching gzip/xz payloads.
- 73 Target unit tests, the hidden sret regression, and two OHOS x86_64
  long-double C ABI guest tests.
- Four host compilers' three-architecture outputs and all three native
  compilers running in OHOS QEMU.

That independent rebuild reused LLVM 22.1.8 / Clang / LLD / zlib / zstd
dependencies built from the same official source base; it did not repeat a
cold LLVM build. The normal fresh checkout command above builds dependencies.
Windows VM validation used the prebuilt runtime kit and did not cover a full
Windows runtime cold build. Some ARMv7 guests stopped responding after all
required success markers; long-term guest stability was not verified.
Validation used the pinned QEMU images with SDK 6.1.1.125 / API 24, and did
not include physical devices.

Local records are retained in `zig-bootstrap/dist/0.17.0/` and
`dist/releases/0.17.0/`: `validation-report.txt` / `.json`,
`archive-verification.json`, `clean-source-verification.json`, and
`validation-logs/`. These are generated records, not tracked repository files.
Keep `out/`, `dist/`, QEMU images, SDK installations, and VM keys out of commits.

## License preservation

Repository-owned additions use [MIT](../LICENSE), matching zig-napi.
[LICENSE-ZIG](../LICENSE-ZIG) is an unchanged copy of the official Zig license;
`zig-bootstrap/zig/LICENSE` and upstream source notices remain in place.
Keep upstream license files and per-file copyright notices when regenerating
overlays or distributing packages. See [third-party notices](../THIRD_PARTY_NOTICES.md#english)
for the scope of each license.
