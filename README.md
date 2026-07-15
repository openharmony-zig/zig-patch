# Zig 0.16.x OpenHarmony 构建与验证

本仓库把 Zig/OpenHarmony 适配整理成可重放的源码 patch、完整构建矩阵和
三架构 QEMU 运行测试。基线固定为官方
[`ziglang/zig-bootstrap`](https://codeberg.org/ziglang/zig-bootstrap.git)
的 `0.16.x` 分支提交：

```text
7e0d1b35dffd18ba7a45c8710ca6fee516641474
```

## 产物矩阵

宿主交叉开发包：

| 名称 | bootstrap target | 可执行文件 |
| --- | --- | --- |
| arm64 macOS | `aarch64-macos-none` | `zig` |
| x64 Linux GNU | `x86_64-linux-gnu` | `zig` |
| x64 Linux musl | `x86_64-linux-musl` | `zig` |
| x64 Windows GNU | `x86_64-windows-gnu` | `zig.exe` |

OHOS 原生 Zig：

| 名称 | target | CPU |
| --- | --- | --- |
| arm64 | `aarch64-linux-ohos` | `baseline` |
| armv7a | `arm-linux-ohoseabi` | `generic+v7a` |
| x86_64 | `x86_64-linux-ohos` | `baseline` |

所有 target、CPU、QEMU 归档名和校验和都由
[`ohos/manifest.json`](zig-bootstrap/ohos/manifest.json) 统一记录。

## 从干净源码重放

```sh
git clone --recurse-submodules <本仓库地址>
cd zig-patch

# 严格检查 0.16.x 基线并应用完整 OHOS patch。
scripts/apply-ohos-patch.sh

# 构建、检查并打包上述七个目标；包和 SHA-256 位于 zig-bootstrap/dist/。
# 归档统一命名为 zig-<target>-<cpu>.tar.xz，例如：
# zig-aarch64-macos-none-baseline.tar.xz
scripts/build-matrix.sh
```

可分组或选择目标：

```sh
scripts/build-matrix.sh --only host
scripts/build-matrix.sh --only native
scripts/build-matrix.sh --only host --targets arm64-macos,x64-linux-musl
scripts/build-matrix.sh --skip-build       # 检查并打包已有 out/zig-* 目录
scripts/build-matrix.sh --skip-package     # 构建/检查但不生成归档
```

同一次矩阵调用会在首个目标成功后自动为后续目标复用 `zig-bootstrap/out/host`。
独立调用也可在确认该目录来自同一份源码后设置 `ZIG_BOOTSTRAP_SKIP_HOST=1`；
并行任务必须使用不同 target，不能共享同一个
`out/build-llvm-<target>-<cpu>` 目录。

## QEMU 真机级验证

准备 `harmony-contrib/ohos-qemu` 的三个发布归档后：

```sh
scripts/test-qemu.sh \
  --zig zig-bootstrap/out/zig-aarch64-macos-none-baseline/zig \
  --packages /path/to/ohos-qemu/packages \
  --native-zig-root zig-bootstrap/out \
  --native-only \
  --arch all
```

测试会校验 QEMU 归档 SHA-256，依次启动 arm64、armv7a、x86_64 的完整
OpenHarmony standard-system guest，并覆盖：

- Zig/C 静态、static-PIE、动态程序和共享库/dlopen；
- 文件、mmap、线程、TLS、原子操作、网络、解析器、时间、locale、数学库；
- OHOS malloc 扩展及 x86_64 IEEE binary128 `long double`；
- 显式 `zig cc`、`zig c++`、`zig ar`、`zig ranlib` 构建产物；
- 三种 OHOS 原生 Zig 的 `version`/`env`，以及 guest 内现场编译并运行 Zig 程序。

原生 Zig 运行验证会由 HDC 直接传输编译器，未压缩 tar 只携带 smoke 所需的
标准库/编译器运行库，避免占用 armv7a guest 的稳定运行窗口；最终发布包仍是
完整前缀。

发布前验证四种宿主包本身，而不只是用 macOS 包代替检查：

```sh
scripts/test-host-matrix.sh \
  --packages /path/to/ohos-qemu/packages \
  --hdc-endpoint 127.0.0.1:5556
```

该脚本原生执行 arm64 macOS Zig，在 amd64 容器中执行 Linux GNU/musl Zig。
Windows GNU Zig 在原生 x86_64 Linux 上通过 WineHQ 11 容器执行；在 arm64
macOS 上则自动使用真实 x86_64 Ubuntu 全系统 QEMU VM + WineHQ 11，避开
Rosetta/Wine 页大小与 NT 线程限制。每个宿主 Zig 都执行 Zig/C/C++ 编译、
`zig ar`、`zig ranlib` 和最终链接；Windows VM 路径使用 control Zig 预建
target runtime kit，但仍由 Windows Zig 实际编译三架构 C/C++、arm64 Zig
探针并生成全部最终 ELF/DSO。其三架构
产物随后分别进入对应 OHOS QEMU。可用 `--targets x64-windows-gnu` 单独重跑，
或加 `--compile-only` 跳过 QEMU；中断后可用 `--skip-compile` 检查并复用
已有测试产物。容器定义固定在
`zig-bootstrap/ohos/Dockerfile.host-test`。

只复现 Windows 编译验证时可直接执行：

```sh
zig-bootstrap/scripts/ohos/prepare-runtime-kit.sh \
  --zig zig-bootstrap/out/zig-aarch64-macos-none-baseline/zig \
  --output zig-bootstrap/out/ohos-runtime-kit

zig-bootstrap/scripts/ohos/test-windows-vm.sh \
  --zig zig-bootstrap/out/zig-x86_64-windows-gnu-baseline/zig.exe \
  --runtime-kit zig-bootstrap/out/ohos-runtime-kit \
  --work-dir zig-bootstrap/out/windows-host-smoke
```

VM 的 cloud image、qcow2 overlay 和 SSH key 默认保存在
`zig-bootstrap/out/ohos-windows-x86-vm/`，后续运行会复用；可用
`--windows-vm-dir` 和 `--windows-vm-port` 调整矩阵脚本中的位置与端口。
完整宿主矩阵会自动让 control Zig 生成带 SHA-256 的 target runtime kit 并传入
VM。kit 不含最终可执行文件；Windows Zig 仍实际执行上述 Zig/C/C++ 编译、
归档和所有最终链接，同时避免 TCG 中数小时的运行库冷构建。

在 arm64 主机上，Linux musl 的静态 Zig 会自动改用原生 arm64 容器中的
`qemu-x86_64`，对应定义为
`zig-bootstrap/ohos/Dockerfile.host-test-arm64`，避免 Rosetta 静态 ELF
子进程死锁；脚本会把该仿真路径限制为两个并发 Zig job。

若 `5555` 已被 DevEco Emulator 占用，可无干扰地另选端口：

```sh
scripts/test-qemu.sh ... --hdc-endpoint 127.0.0.1:5556
```

每个架构默认允许两次完整 clean-boot；失败后会先从校验过的归档恢复可写
QEMU 镜像再重试。可用 `--qemu-attempts 1` 关闭重试。
普通 HDC 命令默认超时为 180 秒；原生 Zig 在 TCG guest 内的冷缓存编译单独
允许 600 秒，可分别通过 `QEMU_HDC_COMMAND_TIMEOUT` 和
`QEMU_NATIVE_HDC_COMMAND_TIMEOUT` 调整。

所有 OHOS 脚本默认使用 `zig-bootstrap/out/tmp` 作为宿主临时目录；需要放到
其他磁盘时可设置 `OHOS_TMPDIR`。

只做编译和 ELF 元数据检查可加 `--compile-only`。完整维护、libc overlay
再生成、OpenLibm f128 更新和日志路径见
[`zig-bootstrap/ohos/README.md`](zig-bootstrap/ohos/README.md)。

## Patch 维护

可复用 patch 是 [`patch/zig-ohos-0.16.x.patch`](patch/zig-ohos-0.16.x.patch)，
只保证应用于上面固定的官方基线。修改子模块中的适配后执行：

```sh
scripts/refresh-patch.sh
```

该脚本使用临时 Git index 导出 `ohos/source-paths.txt` 声明的范围，不会改动
子模块的真实暂存区，并同步生成 SHA-256 文件。
