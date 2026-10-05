# Zig for OpenHarmony

[English](README.md) | 简体中文

支持 OpenHarmony（OHOS）的 Zig **0.17.0**。本仓库提供[完整源码补丁](patch/zig-ohos-0.17.x.patch)、
用于交叉开发的宿主编译器，以及三种 OHOS 架构的原生编译器。补丁基于
Zig 官方 0.17.0 正式发布版本。

工具链包含 OHOS libc、头文件、C/C++ 运行库，以及 OHOS x86_64 的 IEEE
binary128 `long double` 支持。每个宿主编译器均可生成下表中三种 OHOS
架构的程序。

## 下载

从 [GitHub Releases](https://github.com/openharmony-zig/zig-patch/releases)
下载产物。交叉编译请选择**宿主包**，在 OHOS 系统内运行 Zig 请选择**原生包**。

| 类型 | 平台 | Target | CPU | 归档格式 |
| --- | --- | --- | --- | --- |
| 宿主 | macOS ARM64 | `aarch64-macos-none` | `baseline` | `.tar.xz`、`.tar.gz` |
| 宿主 | Linux x86_64 GNU | `x86_64-linux-gnu` | `baseline` | `.tar.xz`、`.tar.gz` |
| 宿主 | Linux x86_64 musl | `x86_64-linux-musl` | `baseline` | `.tar.xz`、`.tar.gz` |
| 宿主 | Windows x86_64 GNU | `x86_64-windows-gnu` | `baseline` | `.tar.xz`、`.tar.gz` |
| 原生 | OHOS ARM64 | `aarch64-linux-ohos` | `baseline` | `.tar.xz` |
| 原生 | OHOS ARMv7 | `arm-linux-ohoseabi` | `generic+v7a` | `.tar.xz` |
| 原生 | OHOS x86_64 | `x86_64-linux-ohos` | `baseline` | `.tar.xz` |

归档命名为 `zig-<target>-<cpu>.tar.xz` 或 `.tar.gz`，每个 xz 包附带
`.tar.xz.sha256` 校验文件。0.17.0 沿用
[0.16.0](https://github.com/openharmony-zig/zig-patch/releases/tag/0.16.0)
的附件名称和格式：七个 xz 包、七个校验文件和四个宿主 gzip 包，共
**18 个上传附件**。两种源码归档由 GitHub 根据发布标签自动生成。

## 快速开始

以 macOS ARM64 为例，下载 xz 包和校验文件后执行：

```sh
shasum -a 256 -c zig-aarch64-macos-none-baseline.tar.xz.sha256
tar -xf zig-aarch64-macos-none-baseline.tar.xz
./zig-aarch64-macos-none-baseline/zig version
```

版本输出应为 `0.17.0`。Linux 可使用 `sha256sum -c <校验文件>`；Windows
包中的可执行文件为 `zig.exe`。请保留编译器旁的完整 `lib/` 目录。

将解压后的宿主包目录加入 `PATH`，即可编译自己的 Zig、C 或 C++ 源码：

```sh
zig build-exe main.zig -target aarch64-linux-ohos -lc -O ReleaseFast
zig cc main.c -target aarch64-linux-ohos -o hello-ohos
zig c++ main.cpp -target aarch64-linux-ohos -o hello-cxx-ohos
```

ARMv7 使用 `arm-linux-ohoseabi -mcpu=generic+v7a`，x86_64 使用
`x86_64-linux-ohos`。生成的程序应在对应架构的 OHOS 设备或系统镜像中运行。

## 构建与贡献

从全新源码构建、维护补丁、整理发布附件和执行 QEMU 测试，请参阅
[开发文档](docs/develop.zh-CN.md)。

验证基线为固定的 OHOS QEMU 镜像及 SDK **6.1.1.125 / API 24**。
[验证范围](docs/develop.zh-CN.md#验证范围)说明了宿主与原生编译器检查、
依赖复用情况及已观察到的限制。

## 许可证

本仓库自有新增内容使用 [MIT](LICENSE)，许可文本及
`2025-present richerfu` 版权声明与
[zig-napi](https://github.com/openharmony-zig/zig-napi/blob/main/LICENSE) 一致。
Zig 原始 MIT 许可及贡献者版权声明逐字保留在 [LICENSE-ZIG](LICENSE-ZIG)。
附带的上游源码仍遵循各自许可，详见[第三方许可说明](THIRD_PARTY_NOTICES.md#简体中文)。
