FROM alpine:latest
LABEL maintainer="VxDxK"

ENV PATH="/root/.cargo/bin:${PATH}"

RUN set -e &&\
    apk add --no-cache --update bash build-base gcc wget git curl cmake python3 curl && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y 

WORKDIR /work
