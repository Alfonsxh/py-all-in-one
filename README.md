# py-all-in-one

`py-all-in-one` 是一个 Python 环境整体打包、分发的项目，有点类似于 pyinstaller。

主要是为了解决 pyinstaller 无法解决的下面场景：**不同操作系统 Python 环境与系统环境的兼容问题**。

Python及其导入的模块，会有很多的动态库依赖(xx.so)，如果这些动态库依赖在打包环境、部署环境不一样，很难通过现有的打包工具解决。

## 🚀 简单使用

### 「1」制作虚拟环境（docker）

使用docker镜像进行打包

```shell
# tree test
test
├── Python
│ ├── Python-2.7.15.tgz
│ ├── Python-2.7.6.tgz
│ └── Python-3.8.18.tgz
└── requirements.txt

# docker run -it --rm --pull always --platform linux/amd64 \
  -v `pwd`/test/Python:/packages/Python \
  -v `pwd`/test/requirements.txt:/packages/requirements.txt \
  -v `pwd`/test/build:/packages/build alfonsxh/py-all-in-one:latest --install-dir /usr/local/python_env/ --project alfonstest --python-version 3.8.18
...
[ OK ]: 包位置：build/alfonstest_x86_64_env.tar.gz
[ OK ]: 打包[成功]！
```

docker参数解释：

- `--platform linux/amd64` - CPU平台，支持 linux/amd64、linux/arm64 两种
- `-v {pwd}/test/Python` - Python安装包位置，打包前需要将Python源码下载保存在该目录。源码下载地址：<https://www.python.org/ftp/python> （当前只支持tgz包）
- `-v {pwd}/test/requirements.txt` - 项目依赖的 Python 模块
- `-v {pwd}/test/build` - 打完包后，保存的目录

项目参数解释：

```shell
usage: build.py [-h] [--install-dir PREFIX] --project PROJECT --python-version
                {3.8.18,2.7.15,2.7.6}

此脚本用于制作Python项目的虚拟环境，支持的Python版本如下：
        - 3.8.18
        - 2.7.15
        - 2.7.6

optional arguments:
  -h, --help            show this help message and exit
  --install-dir PREFIX  指定环境的路径, 默认的环境路径为: /root/.python_env
  --project PROJECT     指定项目的名字
  --python-version {3.8.18,2.7.15,2.7.6}
                        指定python的版本
```

- `--install-dir` - Python 环境安装的目录，对应在部署机器上的路径
- `--project` - 项目名称，虚拟环境会生成在 `{install-dir}/{python_version}/{project}` 目录下。如：`--install-dir /usr/local/python_env/ --project alfonstest --python-version 3.8.18` -> `/usr/local/python_env/3.8.18/alfonstest`
- `--python-version` - Python 版本，根据 `pwd`/test/Python 目录下的Python源码包进行选择。暂时只支持先下载 Python 源码的方式

打完包后，会在映射路径下生成Python环境安装包

```shell
# tree test
test
├── Python
│ ├── Python-2.7.15.tgz
│ ├── Python-2.7.6.tgz
│ └── Python-3.8.18.tgz
├── build
│ └── alfonstest_x86_64_env.tar.gz
└── requirements.txt

# tar -tf test/build/alfonstest_x86_64_env.tar.gz 
alfonstest/
alfonstest/system_lib.tar.gz
alfonstest/install.sh
alfonstest/alfonstest_env_virtual.tar.gz
```

### 「2」部署及使用

拷贝压缩包到环境中，解压后执行 `install.sh`。

```shell
[root@cf93a868310e tmp]# python --version
Python 2.7.5
[root@cf93a868310e tmp]# tar -xzf alfonstest_x86_64_env.tar.gz 
[root@cf93a868310e tmp]# cd alfonstest
[root@cf93a868310e alfonstest]# ll
total 50548
-rw-r--r-- 1 root root 44059611 Jan 15 19:13 alfonstest_env_virtual.tar.gz
-rw-r--r-- 1 root root      175 Jan 15 19:13 install.sh
-rw-r--r-- 1 root root  7696283 Jan 15 19:13 system_lib.tar.gz
[root@cf93a868310e alfonstest]# bash ./install.sh 
...
[root@cf93a868310e alfonstest]# source /usr/local/python_env/3.8.18/alfonstest/bin/activate
(alfonstest) [root@cf93a868310e alfonstest]# python --version
Python 3.8.18
```

## 📖 原理

- [Python虚拟环境制作](./docs/Python虚拟环境制作.md)

> 核心：修改可执行程序及动态库的 rpath 路径

## ⚠️ 无法覆盖的场景

通过本项目打出来的 Python 虚拟环境，可能会出现 glibc 版本与 `Linux 操作系统内核不匹配` 的问题。可以通过改变打包镜像的方式进行解决。
