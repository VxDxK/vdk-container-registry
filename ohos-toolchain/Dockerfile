FROM ubuntu:24.10

ENV PATH="/sdk/native/llvm/python3/bin:/sdk/native/build-tools/cmake/bin:/scripts:/root/.cargo/bin:${PATH}"

WORKDIR /sdk
COPY ohos-sdk-windows_linux-public.tar.gz install_sdk.sh ./ 

RUN apt-get update && \
    apt-get install -y --no-install-recommends unzip curl ca-certificates && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    rustup target add aarch64-unknown-linux-ohos && \
    rm -rf /var/lib/apt/lists/* && \
    ./install_sdk.sh && rm -rf ./install_sdk.sh 


COPY config.toml /root/.cargo
COPY scripts /scripts

ENV CC=/scripts/aarch64-unknown-linux-ohos-clang.sh \
    CXX=/scripts/aarch64-unknown-linux-ohos-clang++.sh \
    LD=/sdk/native/llvm/bin/lld \
    AS=/sdk/native/llvm/bin/llvm-as \
    AR=/sdk/native/llvm/bin/llvm-ar 

# ENV CMAKE_TOOLCHAIN_FILE=/sdk/native/build/cmake/ohos.toolchain.cmake 

WORKDIR /work
