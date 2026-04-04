FROM alpine:latest
LABEL maintainer="VxDxK"

ARG XRAY_CORE_VERSION=v26.3.27
ENV XRAY_LOCATION_ASSET=/opt/xray/asset

RUN set -e &&\
    # apk add --no-cache bash &&\
    wget https://github.com/XTLS/Xray-core/releases/download/${XRAY_CORE_VERSION}/Xray-linux-64.zip &&\
    mkdir -p ${XRAY_LOCATION_ASSET} && \
    unzip ./Xray-linux-64.zip -d /opt/xray  &&\
    rm -rf Xray-linux-64.zip && \
    rm /opt/xray/LICENSE && \
    rm /opt/xray/README.md && \
    rm /opt/xray/geo*.dat

WORKDIR /opt/xray

CMD [ "/opt/xray/xray", "run", "-config", "/config.json" ]
