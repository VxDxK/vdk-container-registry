#!/bin/sh
exec /sdk/native/llvm/bin/clang++ \
  -target aarch64-linux-ohos \
  --sysroot=/sdk/native/sysroot \
  -D__MUSL__ \
  "$@"
