

# py-all-in-one

`py-all-in-one` is a project for bundling and distributing complete Python environments, somewhat similar to PyInstaller.

It primarily aims to solve a scenario that PyInstaller cannot handle: **compatibility issues between the Python environment and the system environment across different operating systems**.

Python and its imported modules rely heavily on dynamic libraries (`.so` files). If these dynamic library dependencies differ between the build environment and the deployment environment, it is difficult to resolve using existing packaging tools.

The Python virtual environment package created by this project can run on multiple Linux operating systems (Red Hat, CentOS, Ubuntu, etc.) and across various OS versions, eliminating the need to worry about system dynamic library dependencies!

## 🚀 Quick Start

### 「1」 Create Virtual Environment (Docker)

Use a Docker image for packaging:

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
[ OK ]: Package location: build/alfonstest_x86_64_env.tar.gz
[ OK ]: Packaging [Success]!
```

Docker parameter explanations:

- `--platform linux/amd64` - CPU architecture, supports `linux/amd64` and `linux/arm64`
- `-v {pwd}/test/Python` - Location of the Python installation package. Before packaging, you need to download and save the Python source code in this directory. Source download URL: <https://www.python.org/ftp/python> (currently only supports `.tgz` packages)
- `-v {pwd}/test/requirements.txt` - Python modules required by the project
- `-v {pwd}/test/build` - Directory where the package will be saved after building

Project parameter explanations:

```shell
usage: build.py [-h] [--install-dir PREFIX] --project PROJECT --python-version
                {3.8.18,2.7.15,2.7.6}

This script is used to create a Python virtual environment for a project. Supported Python versions are:
        - 3.8.18
        - 2.7.15
        - 2.7.6

optional arguments:
  -h, --help            show this help message and exit
  --install-dir PREFIX  Specify the environment path. Default path: /root/.python_env
  --project PROJECT     Specify the project name
  --python-version {3.8.18,2.7.15,2.7.6}
                        Specify the Python version
```

- `--install-dir` - Directory for installing the Python environment, corresponding to the path on the deployment machine
- `--project` - Project name. The virtual environment will be generated in the `{install-dir}/{python_version}/{project}` directory. Example: `--install-dir /usr/local/python_env/ --project alfonstest --python-version 3.8.18` -> `/usr/local/python_env/3.8.18/alfonstest`
- `--python-version` - Python version, selected based on the Python source package in the `pwd`/test/Python directory. Currently, only downloading the Python source code beforehand is supported.

After packaging, the Python environment installation package will be generated in the mapped directory:

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

### 「2」 Deployment & Usage

Copy the compressed archive to the target environment, extract it, and run `install.sh`.

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

## 📖 How It Works

- [Creating Python Virtual Environments](./docs/Python虚拟环境制作.md)

> Core mechanism: Modifies the `rpath` of executables and dynamic libraries.

## ⚠️ Limitations

The Python virtual environment packaged by this project may encounter issues where the glibc version is `incompatible with the Linux OS kernel`. This can be resolved by changing the packaging Docker image.
