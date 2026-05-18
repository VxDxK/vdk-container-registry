FROM ubuntu:26.04

ARG GCC_VERSION=16
ARG CLANG_VERSION=22
ARG CMAKE_VERSION=4.3.2

COPY ./toolchains /toolchains
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    wget \
    gnupg \
    software-properties-common \
    build-essential \
    ninja-build \
    git \
    curl \
    python3 \
    python3-pip \
    libssl-dev \
    gcc-${GCC_VERSION} g++-${GCC_VERSION} \
    clang-${CLANG_VERSION} lld-${CLANG_VERSION} libc++-${CLANG_VERSION}-dev libc++abi-${CLANG_VERSION}-dev \
    llvm-${CLANG_VERSION}-dev libclang-${CLANG_VERSION}-dev \
    && rm -rf /var/lib/apt/lists/* \
    && update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-${GCC_VERSION} 100 \
    && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-${GCC_VERSION} 100 \
    && update-alternatives --install /usr/bin/clang clang /usr/bin/clang-${CLANG_VERSION} 100 \
    && update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-${CLANG_VERSION} 100 \
    && wget -O cmake.sh "https://github.com/Kitware/CMake/releases/download/v${CMAKE_VERSION}/cmake-${CMAKE_VERSION}-linux-x86_64.sh" \
    && chmod +x cmake.sh \
    && ./cmake.sh --skip-license --prefix=/usr/local \
    && rm cmake.sh \
    && git clone --depth 1 --branch clang_${CLANG_VERSION} https://github.com/include-what-you-use/include-what-you-use.git /tmp/iwyu \
    && cd /tmp/iwyu \
    && cmake -S. -Bbuild -GNinja -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH=/usr/lib/llvm-${CLANG_VERSION} \
    && cmake --build build/ --target install --parallel \
    && cd / && rm -rf /tmp/iwyu

WORKDIR /work
CMD ["/bin/bash"]