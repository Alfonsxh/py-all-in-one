# py-all-in-one

`py-all-in-one` 是一个 python 环境整体打包的项目，解决下面场景中 Python 环境的部署问题：

- 无公网环境
- 不同操作系统python环境的兼容问题

## 使用

### 「1」制作虚拟环境
    
使用docker镜像进行打包

```shell
# tree test
test
├── Python
│ ├── Python-2.7.15.tgz
│ ├── Python-2.7.6.tgz
│ └── Python-3.8.18.tgz
└── requirements.txt

# docker run -it --rm --platform linux/amd64 \
  -v `pwd`/test/Python:/packages/Python \
  -v `pwd`/test/requirements.txt:/packages/requirements.txt \
  -v `pwd`/test/build:/packages/build lfonsxh/py-all-in-one:latest --install-dir /usr/local/python_env/ --project alfonstest --python-version 3.8.18
...
[ OK ]: 包位置：build/alfonstest_x86_64_env.tar.gz
[ OK ]: 打包[成功]！
```

位置解释：

- `pwd`/test/Python - Python安装包位置，打包前需要将Python源码下载保存在该目录。源码下载地址：https://www.python.org/ftp/python/ （当前只支持tgz包）
- `pwd`/test/requirements.txt - 项目依赖的 Python 模块
- `pwd`/test/build - 打完包后，保存的目录

打包参数解释：

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

- `--install-dir` - Python 环境安装的目录
- `--project` - 项目名称
- `--python-version` - Python 版本，根据 `pwd`/test/Python 目录下的Python源码包进行选择

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

## 无法覆盖的场景

可能会出现 glibc 版本与 操作系统内核不匹配 的问题