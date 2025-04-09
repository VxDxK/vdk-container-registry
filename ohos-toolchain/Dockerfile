FROM ubuntu:24.10

ENV PATH="/scripts:/root/.cargo/bin:${PATH}"

WORKDIR /sdk
COPY ohos-sdk-windows_linux-public.tar.gz .
COPY install_sdk.sh .

RUN apt-get update && \
    apt-get install -y --no-install-recommends unzip curl ca-certificates && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    rustup target add aarch64-unknown-linux-ohos && \
    rm -rf /var/lib/apt/lists/* && \
    ./install_sdk.sh && rm -rf ./install_sdk.sh 


COPY config.toml /root/.cargo
COPY scripts /scripts

WORKDIR /work
