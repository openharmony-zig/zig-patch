# 开发文档

[English](develop.md) | 简体中文 | [README](../README.zh-CN.md)

本文说明本地源码适配、构建、打包和验证流程。除非另有说明，所有命令均在
**zig-patch 仓库根目录**执行。

## 源码基线与目录

`zig-bootstrap` 子模块固定在官方 **0.17.0** 正式发布标签、`0.17.x` 分支的
以下提交：

```text
b12ab1fbafc3a290d6a13c42b14e1c67dd826c0f
```

官方发布日期为 2026-10-01。[官方版本索引](https://ziglang.org/download/index.json)
提供 bootstrap 归档及校验和；应用补丁后，
`zig-bootstrap/ohos/manifest.json` 中也记录了这些固定信息。

| 路径 | 用途 |
| --- | --- |
| `patch/zig-ohos-0.17.x.patch` 及 `.sha256` | 完整 OHOS 补丁及校验和 |
| `scripts/` | 仓库入口脚本和本地发布附件整理 |
| `zig-bootstrap/ohos/manifest.json` | 版本、源码 revision、target/CPU 矩阵、QEMU 镜像校验和 |
| `zig-bootstrap/ohos/source-paths.txt` | 导出补丁的源码范围 |
| `zig-bootstrap/scripts/ohos/` | 构建、维护与验证脚本实现 |
| `zig-bootstrap/zig/lib/libc/ohos/` | OHOS libc overlay 和 OpenLibm binary128 源码 |
| `zig-bootstrap/zig/test/ohos/` | 运行库与编译器 smoke 测试 |
| `zig-bootstrap/out/`、`zig-bootstrap/dist/`、`dist/` | 生成的构建目录、归档和报告 |

子模块中的 OHOS 专用路径由补丁创建，执行 `scripts/apply-ohos-patch.sh`
后才可访问。应用补丁后的 `ohos/README.md` 也说明了内部脚本，其示例以
子模块根目录为工作目录。

## 从全新源码构建

本地需要 Git、C/C++ 编译器、CMake、Ninja、jq、ripgrep、xz 和 Python 3，
使用类 Unix 构建环境。完整补丁包含 OHOS libc、头文件、OpenLibm 源码及
构建脚本，常规构建无需已有构建目录或外部 OHOS SDK 安装。重新生成
overlay 时才需要对应的 SDK 和 musl 源码。

```sh
git clone --branch 0.17.0 --recurse-submodules https://github.com/openharmony-zig/zig-patch.git
cd zig-patch
scripts/apply-ohos-patch.sh
CMAKE_GENERATOR=Ninja CMAKE_BUILD_PARALLEL_LEVEL=6 scripts/build-matrix.sh
```

示例使用发布后的 `0.17.0` 标签；准备发布时可改为对应适配分支。
已有 clone 应先切换到需要的分支或标签，再执行
`git submodule update --init --recursive`，初始化该提交记录的子模块，
再应用补丁。应用脚本检查精确的 bootstrap 基线，并支持重复执行；根目录
的构建和测试入口也会先调用它。

完整矩阵包含四个宿主编译器和三个 OHOS 原生编译器。流程先构建宿主
LLVM/Clang/LLD 和 Zig，再构建目标依赖，最后构建并安装目标 Zig 编译器、
库文件及文档。安装前缀为 `zig-bootstrap/out/zig-<target>-<cpu>/`，xz 包和
校验文件输出到 `zig-bootstrap/dist/`。归档顶层目录与包名一致，ARMv7
明确使用 `generic+v7a`。

可选择分组或 manifest 中的目标名称：

```sh
scripts/build-matrix.sh --only host
scripts/build-matrix.sh --only native
scripts/build-matrix.sh --only host --targets arm64-macos,x64-linux-musl
scripts/build-matrix.sh --skip-build
scripts/build-matrix.sh --skip-package
```

`--skip-build` 检查并打包已有前缀，包含已安装 OHOS 库源码是否过期的检查；
`--skip-package` 仅构建与检查。一次矩阵调用在首个目标成功后自动为后续
目标复用 `zig-bootstrap/out/host`。独立调用确认该宿主前缀来自同一源码后，
可设置 `ZIG_BOOTSTRAP_SKIP_HOST=1`。并行构建必须使用不同 target，不能
共享 `out/build-llvm-<target>-<cpu>`。

所有 OHOS 脚本默认将宿主临时文件放在 `zig-bootstrap/out/tmp`，可通过
`OHOS_TMPDIR` 改到其他磁盘。

## 整理发布附件

```sh
python3 scripts/prepare-release.py
```

脚本读取 `zig-bootstrap/dist/` 的归档，核对 bootstrap 基线、归档校验和、
编译器是否存在、完整 manifest 及构建元数据，随后生成与 0.16.0 一致的
18 个附件：

- 七个 `.tar.xz` 包及七个 `.tar.xz.sha256` 文件。
- 四个宿主 `.tar.gz` 包，其解压后的 tar 数据与对应 xz 包完全一致。

上传附件目录为 `dist/releases/0.17.0/assets/`。旁边的 `SHA256SUMS` 和
`release-assets.json` 记录全部 18 个文件。GitHub 自动生成的两种源码
归档由发布标签提供。

使用本次已验证并保留的版本化归档时执行：

```sh
python3 scripts/prepare-release.py --source-dir zig-bootstrap/dist/0.17.0
```

脚本还支持 `--only`、`--targets` 和 `--output-dir`；选择不同目标集合时，
请使用独立输出目录。构建产物与验证记录均为本地生成文件，全新 clone
不会包含它们。

## 维护补丁

修改 `zig-bootstrap` 中的适配源码后导出补丁：

```sh
scripts/refresh-patch.sh
```

脚本使用临时 Git index 导出 `zig-bootstrap/ohos/source-paths.txt` 声明的
范围，同步更新补丁 SHA-256，不会改动子模块的真实暂存区。子模块保持在
官方基线提交，已应用的源码改动由导出补丁携带。

使用新构建的宿主编译器检查源码结构、Shell 语法、Zig 格式和三个目标探针：

```sh
zig-bootstrap/scripts/ohos/check-source.sh \
  --zig zig-bootstrap/out/zig-aarch64-macos-none-baseline/zig
```

升级 Zig 基线时，先对照目标 release 审查适配，再更新子模块 gitlink、
`.gitmodules`、应用与导出脚本中的基线常量、manifest 及源码检查，随后
重新导出补丁并在全新 checkout 上验证。当前补丁仅保证适用于固定基线。

0.17.0 适配包含 `cc_dir` API 迁移、PIE 策略入口整合、OHOS DNS 查询表
类型和 ARMv7 fortify 兼容修复、binary128 `long double` ABI 支持，以及
LLVM 隐藏 sret 参数计数修复。升级编译器时应保留相应 C/Zig ABI 回归测试。

## 重新生成 libc 与头文件

OHOS libc 是相对 Zig musl 的 overlay，OHOS 头文件由固定 SDK 生成。
先准备 `zig-bootstrap/ohos/manifest.json` 记录的 musl revision 和 SDK
版本，再生成并比较，不修改已签入的 overlay：

```sh
zig-bootstrap/scripts/ohos/update-libc.sh \
  --zig zig-bootstrap/out/zig-aarch64-macos-none-baseline/zig \
  --musl-source /path/to/third_party_musl \
  --sdk-native /path/to/ohos-sdk/native
```

存在差异时命令返回非零，差异保存在
`zig-bootstrap/out/ohos-maintenance/diff/`。审查后重复命令并加 `--apply`
同步源码，此时需要 `rsync`。按需更新生成器 fixup 和编译器 glue，执行
源码与三架构运行检查，再刷新补丁；升级上游依赖时同步更新 manifest。
musl 许可文本位于 `zig-bootstrap/zig/lib/libc/musl/COPYRIGHT`。

## 更新 binary128 OpenLibm

OHOS x86_64 的 `long double` 为 IEEE binary128。OpenLibm `v0.8.7` 子树
替换不兼容的 x87 long-double 源码，由
`zig-bootstrap/zig/src/libs/ohos.zig` 显式选入。精确 revision 和兼容补丁
记录在 manifest 中。

```sh
git clone https://github.com/JuliaMath/openlibm.git /path/to/openlibm
git -C /path/to/openlibm switch --detach 9fbeafcd4f1b6ef6aa3946c1c8faead50f38a94d
zig-bootstrap/scripts/ohos/update-openlibm.sh --source /path/to/openlibm
```

先审查 `zig-bootstrap/out/ohos-openlibm-maintenance/diff/`，再加
`--apply`。x86_64 QEMU 测试会实际执行 `powl`、`expl`、`logl`、`sqrtl`，
并要求出现 `C_OHOS_F128_OK` 标记。

## QEMU 验证

准备 [harmony-contrib/ohos-qemu](https://github.com/harmony-contrib/ohos-qemu)
的三个镜像归档，以及 QEMU 和 HDC。镜像 revision 和 SHA-256 必须与
manifest 中的固定值一致。脚本校验归档后，依次启动完整 OpenHarmony
standard-system 客体。

验证四个宿主编译器：

```sh
scripts/test-host-matrix.sh \
  --packages /path/to/ohos-qemu/packages \
  --hdc-endpoint 127.0.0.1:5556
```

矩阵使用每个宿主编译器生成三个 OHOS 架构的程序，并在对应客体运行。
覆盖静态、static-PIE、动态程序、共享库/dlopen、malloc 扩展、文件、
mmap、线程、TLS、原子操作、网络/DNS、时间、locale、数学库，以及
`zig cc`、`zig c++`、`zig ar` 和 `zig ranlib`。

macOS ARM64 编译器在本机原生执行。Linux 编译器在容器内执行；ARM64
宿主上的静态 musl 编译器使用 ARM64 容器内的 `qemu-x86_64`，限制为两个
Zig job。Windows 编译器通过 x86_64 Linux 环境中的 WineHQ 11 执行；
ARM64 macOS 使用完整 x86_64 Ubuntu QEMU VM。宿主容器验证需要 Docker，
定义位于 `zig-bootstrap/ohos/Dockerfile.host-test` 和
`Dockerfile.host-test-arm64`。

可用 `--targets x64-windows-gnu` 单独验证宿主；`--compile-only` 只做编译
和 ELF 检查，`--skip-compile` 核对并复用已有产物重跑 QEMU，后两项不能
同时使用。VM 状态及 SSH key 默认保存在
`zig-bootstrap/out/ohos-windows-x86-vm/`，可用 `--windows-vm-dir` 和
`--windows-vm-port` 调整位置和转发的 SSH 端口。

验证三个 OHOS 原生编译器：

```sh
scripts/test-qemu.sh \
  --zig zig-bootstrap/out/zig-aarch64-macos-none-baseline/zig \
  --packages /path/to/ohos-qemu/packages \
  --native-zig-root zig-bootstrap/out \
  --native-only \
  --arch all \
  --hdc-endpoint 127.0.0.1:5556
```

每个原生编译器执行 `version`、`env` 和客体内 Zig 编译、链接、运行检查，
要求出现 `NATIVE_ZIG_OHOS_OK`。`--native-only` 为这些检查单独 clean-boot。
HDC 直接传输编译器及 smoke 所需的精简库 tar，发布归档始终保留完整安装
前缀。去掉 `--native-only` 可在同次启动中加入交叉编译的运行库 smoke。
仅检查编译和 ELF 元数据时执行：

```sh
scripts/test-qemu.sh \
  --zig zig-bootstrap/out/zig-aarch64-macos-none-baseline/zig \
  --compile-only
```

### Windows VM 检查

独立复现 Windows 编译验证：

```sh
zig-bootstrap/scripts/ohos/prepare-runtime-kit.sh \
  --zig zig-bootstrap/out/zig-aarch64-macos-none-baseline/zig \
  --output zig-bootstrap/out/ohos-runtime-kit

zig-bootstrap/scripts/ohos/test-windows-vm.sh \
  --zig zig-bootstrap/out/zig-x86_64-windows-gnu-baseline/zig.exe \
  --runtime-kit zig-bootstrap/out/ohos-runtime-kit \
  --work-dir zig-bootstrap/out/windows-host-smoke
```

control 编译器预建带校验和的 target runtime kit，包含 CRT、libc/libc++、
compiler-rt 和大量使用 std 的 Zig smoke 对象。Windows Zig 编译三架构
C/C++ 和 ARM64 Zig 探针，运行 `ar`/`ranlib` 并完成最终 ELF/DSO 链接。
kit 不含最终可执行文件，宿主矩阵会自动准备它。隔离的 Wine runner 设置
`ZIG_WINE_FILE_LOCK_WORKAROUND=1`，兼容 Wine 尚未完整实现的 `NtLockFile`。

### 客体控制与日志

默认 HDC endpoint 为 `127.0.0.1:5555`；DevEco Emulator 占用 5555 时，
可选择 `127.0.0.1:5556`。每架构默认允许两次 clean-boot，每次尝试前
从已校验归档恢复可写镜像。`--qemu-attempts 1` 关闭重试。

| 环境变量 | 默认值 | 范围或用途 |
| --- | --- | --- |
| `QEMU_HDC_COMMAND_TIMEOUT` | 180 秒 | 普通 HDC 命令，30–600 秒 |
| `QEMU_NATIVE_HDC_COMMAND_TIMEOUT` | 600 秒 | 原生编译器检查，180–1800 秒 |
| `OHOS_TMPDIR` | `zig-bootstrap/out/tmp` | 宿主临时目录 |

构建结果位于 `zig-bootstrap/out/ohos-matrix/build-results.tsv`，宿主矩阵
结果位于 `zig-bootstrap/out/ohos-host-matrix-test/host-results.tsv`，独立
QEMU 日志位于 `zig-bootstrap/out/ohos-qemu-test/`。

## 验证范围

0.17.0 本地验证完成了：

- 完整补丁在官方基线上干净重放，1,441 个适配文件一致。
- 从全新源码和空 Zig 缓存重建七个平台的编译器、库文件与文档；全部
  编译器及每包 20,882 个库文件均与已通过运行验证的产物逐字节一致。
- 七个 xz 包、18 个发布附件的元数据、校验和及 gzip/xz 内容一致性检查。
- 73 项 Target 单元测试、隐藏 sret 回归和两个 OHOS x86_64 long double
  C ABI 客体测试。
- 四个宿主编译器的三架构产物，以及三个原生编译器的 OHOS QEMU 运行检查。

独立源码重建复用了从同一正式版源码构建的 LLVM 22.1.8 / Clang / LLD /
zlib / zstd 依赖，未重复冷构建 LLVM；上文常规全新 checkout 命令会构建
依赖。Windows VM 验证使用预建 runtime kit，未覆盖 Windows 侧完整运行库
冷构建。部分 ARMv7 客体在全部必要成功标记出现后失去响应，未验证长期
稳定性。验证基线为固定 QEMU 镜像和 SDK 6.1.1.125 / API 24，未包含
实体设备测试。

本地记录保存在 `zig-bootstrap/dist/0.17.0/` 和 `dist/releases/0.17.0/`，
包含 `validation-report.txt` / `.json`、`archive-verification.json`、
`clean-source-verification.json` 及 `validation-logs/`。这些记录属于生成
文件，不随仓库签入。提交时应排除 `out/`、`dist/`、QEMU 镜像、本地 SDK
和 VM key。

## 保留许可证

本仓库自有新增内容使用与 zig-napi 一致的 [MIT](../LICENSE)。
[LICENSE-ZIG](../LICENSE-ZIG) 为官方 Zig 许可的原样副本，
`zig-bootstrap/zig/LICENSE` 和上游源码版权声明均保留原样。
重新生成 overlay 或分发产物时，应保留上游许可文件及各文件的版权声明。
各许可证的适用范围见[第三方许可说明](../THIRD_PARTY_NOTICES.md#简体中文)。
