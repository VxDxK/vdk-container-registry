FROM alpine:latest
LABEL maintainer="VxDxK"

ARG XRAY_CORE_VERSION=v25.3.6
ARG T2S_VERSION=v2.5.2

RUN set -e &&\
    apk add --no-cache bash &&\
    wget https://github.com/XTLS/Xray-core/releases/download/${XRAY_CORE_VERSION}/Xray-linux-64.zip &&\
    wget https://github.com/xjasonlyu/tun2socks/releases/download/${T2S_VERSION}/tun2socks-linux-amd64.zip &&\
    unzip ./Xray-linux-64.zip -d /opt/xray  &&\
    rm -rf Xray-linux-64.zip && \
    rm /opt/xray/LICENSE && \
    rm /opt/xray/README.md && \
    rm /opt/xray/geo*.dat && \
    unzip ./tun2socks-linux-amd64.zip -d /opt/tun2socks && \
    rm -rf tun2socks-linux-amd64.zip

WORKDIR /opt/xray
COPY run_core.sh .

CMD [ "/bin/bash","./run_core.sh" ]
