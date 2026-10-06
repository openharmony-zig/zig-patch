# License and third-party notices

[English](#english) | [简体中文](#简体中文)

## English

### Repository additions

Original additions maintained in this repository, including its original
scripts, documentation, and adaptation code, use the [MIT license](LICENSE).
The license text and `Copyright (c) 2025-present richerfu` notice match
[zig-napi](https://github.com/openharmony-zig/zig-napi/blob/main/LICENSE).
Existing upstream code, copied code, and patch context retain their original
copyrights and license terms.

### Zig

[LICENSE-ZIG](LICENSE-ZIG) is a byte-for-byte copy of
`zig-bootstrap/zig/LICENSE` from the official Zig 0.17.0 bootstrap base
`b12ab1fbafc3a290d6a13c42b14e1c67dd826c0f`. It preserves the MIT (Expat)
license and the `Zig contributors` copyright notice. The original submodule
file is unchanged. Installed Zig distributions retain that upstream `LICENSE`.

### Bundled components

Paths below are relative to `zig-bootstrap/`; OHOS overlay paths become
available after applying the patch. This table is a navigation aid. Each
component's full upstream notices and per-file terms remain authoritative.

| Component | License information | Preserved source location |
| --- | --- | --- |
| LLVM, Clang, LLD | Apache-2.0 with LLVM exceptions and included third-party notices | `llvm/LICENSE.TXT`, `clang/LICENSE.TXT`, `lld/LICENSE.TXT` |
| musl and OHOS libc/header overlays | musl MIT license, with additional upstream per-file notices | `zig/lib/libc/musl/COPYRIGHT`; notices in `zig/lib/libc/ohos/` and `zig/lib/libc/include/` |
| OpenLibm binary128 sources | Upstream per-file notices, including BSD and Sun/Moshier permission notices | File headers under `zig/lib/libc/ohos/openlibm/` |
| libc++, libc++abi, libunwind, libtsan | Upstream license texts and component notices | `zig/lib/libcxx/LICENSE.TXT`, `zig/lib/libcxxabi/LICENSE.TXT`, `zig/lib/libunwind/LICENSE.TXT`, `zig/lib/libtsan/LICENSE.TXT` |
| zlib | zlib license | `zlib/LICENSE` |
| zstd | Upstream BSD license text and applicable source notices | `zstd/LICENSE` |
| Other bundled libc/platform sources | Their own upstream license and copyright notices | For example, `zig/lib/libc/glibc/LICENSES`, `zig/lib/libc/mingw/COPYING`, `zig/lib/libc/wasi/LICENSE`, `zig/lib/libc/freebsd/COPYRIGHT` |

Keep the applicable license texts, copyright notices, and source headers with
redistributed source and binary packages. The repository MIT license covers
its original additions and does not replace the licenses of bundled components.

## 简体中文

### 仓库新增内容

本仓库维护的自有新增内容，包括自有脚本、文档与适配代码，使用
[MIT 许可](LICENSE)。许可文本及 `Copyright (c) 2025-present richerfu`
声明与 [zig-napi](https://github.com/openharmony-zig/zig-napi/blob/main/LICENSE)
一致。原有上游源码、拷贝的源码及补丁上下文保留各自原始版权和许可条款。

### Zig

[LICENSE-ZIG](LICENSE-ZIG) 逐字复制官方 Zig 0.17.0 bootstrap 基线
`b12ab1fbafc3a290d6a13c42b14e1c67dd826c0f` 中的
`zig-bootstrap/zig/LICENSE`，保留 MIT（Expat）全文及 `Zig contributors`
版权声明。子模块中的原始文件未修改，已安装的 Zig 发行目录也保留上游
`LICENSE`。

### 附带组件

下列路径均相对于 `zig-bootstrap/`；OHOS overlay 路径在应用补丁后创建。
此表提供许可文件索引，各组件的完整上游声明及逐文件条款仍是依据。

| 组件 | 许可信息 | 保留位置 |
| --- | --- | --- |
| LLVM、Clang、LLD | Apache-2.0、LLVM exceptions 及附带第三方声明 | `llvm/LICENSE.TXT`、`clang/LICENSE.TXT`、`lld/LICENSE.TXT` |
| musl 及 OHOS libc/头文件 overlay | musl MIT 及其他上游逐文件声明 | `zig/lib/libc/musl/COPYRIGHT`；`zig/lib/libc/ohos/`、`zig/lib/libc/include/` 内的声明 |
| OpenLibm binary128 源码 | 上游逐文件许可，包括 BSD、Sun/Moshier 授权声明 | `zig/lib/libc/ohos/openlibm/` 内的文件头 |
| libc++、libc++abi、libunwind、libtsan | 上游许可文本和组件声明 | `zig/lib/libcxx/LICENSE.TXT`、`zig/lib/libcxxabi/LICENSE.TXT`、`zig/lib/libunwind/LICENSE.TXT`、`zig/lib/libtsan/LICENSE.TXT` |
| zlib | zlib 许可 | `zlib/LICENSE` |
| zstd | 上游 BSD 许可及适用的源码声明 | `zstd/LICENSE` |
| 其他 libc/平台源码 | 各自上游许可与版权声明 | 例如 `zig/lib/libc/glibc/LICENSES`、`zig/lib/libc/mingw/COPYING`、`zig/lib/libc/wasi/LICENSE`、`zig/lib/libc/freebsd/COPYRIGHT` |

分发源码和二进制包时，应保留适用的许可全文、版权声明和源码文件头。
仓库 MIT 许可适用于自有新增内容，不替代附带组件的原始许可。
