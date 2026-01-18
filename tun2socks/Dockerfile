FROM alpine:latest
LABEL maintainer="VxDxK"

ARG T2S_VERSION=v2.6.0
WORKDIR /opt

RUN set -e &&\
    wget https://github.com/xjasonlyu/tun2socks/releases/download/${T2S_VERSION}/tun2socks-linux-amd64-v3.zip &&\
    unzip ./tun2socks-linux-amd64*.zip -d /opt/tun2socks && \
    rm -rf tun2socks-linux-amd64*.zip && \
    mv tun2socks/tun2socks-linux* . && \
    rm -rf tun2socks && \
    mv tun2socks-linux* tun2socks
