FROM --platform=$TARGETPLATFORM centos:7 as build

# 多平台构建：https://www.docker.com/blog/faster-multi-platform-builds-dockerfile-cross-compilation-guide/
ARG TARGETARCH

LABEL authors=Alfonsxh

WORKDIR /packages

ADD packages/build.py /packages/build.py
ADD packages/install.sh /packages/install.sh
ADD packages/pip.conf /etc/pip.conf
ADD packages/patchelf_$TARGETARCH /packages/patchelf
ADD packages/CentOS-Base-$TARGETARCH.repo /etc/yum.repos.d/CentOS-Base.repo

RUN echo "Begin build" \

    # 设置时区等参数
    && /usr/bin/cp -f /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo 'Asia/Shanghai' > /etc/timezone \

    # 安装编译环境
    && yum -y install --nogpgcheck gcc gcc-c++ zlib zlib-devel libffi-devel \
        kernel-devel kenel-headers make autoconf libtool bzip2 \
        zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel \
        readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel \
    && yum -y clean all --enablerepo='*'
