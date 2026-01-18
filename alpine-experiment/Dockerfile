FROM alpine:latest
LABEL maintainer="VxDxK"

RUN apk update && apk add --no-cache \
    iputils \
    iptables \
    iproute2 \
    net-tools \
    bind-tools \
    curl \
    wget \
    nano \
    tcpdump \
    traceroute \
    netcat-openbsd \
    && rm -rf /var/cache/apk/*

WORKDIR /work
