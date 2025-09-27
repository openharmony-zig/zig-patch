# Zig patch for OpenHarmony

This project allow us to build zig that can build dynamic or use `zig cc` for OpenHarmony.

For now, we use the default logic of `musl` to link libc or other logic. It may has some issues, but we need more examples or projects to test it.

If you find some codes or logic need to adapt, you can submit a new issue or PR. 

## How to build

Apply the git [patch](./patch/zig-patch.patch) to zig's source code and build it.

For example, you can apply it to `zig-bootstrap` the sub-folder named `zig`. And Using zig-bootstrap to build zig with your target.

## Platform

- [x] Macos
- [ ] Windows
- [ ] Linux