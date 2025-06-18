FROM ubuntu:24.04
LABEL maintainer="VxDxK"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    iputils-ping \
    iptables \
    iproute2 \
    net-tools \
    dnsutils \
    curl \
    wget \
    nano \
    tcpdump \
    traceroute \
    netcat-traditional \
    inetutils-traceroute \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /work
