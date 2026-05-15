FROM docker.io/library/ubuntu:26.04

RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y upgrade \
    && apt-get -y install git gnupg curl python3-pytest python3-pytest-asyncio python3-pytest-cov python3-pytest-httpx python3-httpx python3-debugpy gh nodejs npm
