# 制作独立的 Python 虚拟环境

虚拟环境为运行Python项目的理想环境，可以有效的与系统Python环境进行隔离，每个项目都可以有一个干净的环境运行。

## Python虚拟环境创建

Python虚拟环境的创建，按照Python3的方式，通过 `venv` 模块进行创建。

```shell
python3 -m venv --help                   
usage: venv [-h] [--system-site-packages] [--symlinks | --copies] [--clear] [--upgrade]
            [--without-pip] [--prompt PROMPT]
            ENV_DIR [ENV_DIR ...]

Creates virtual Python environments in one or more target directories.

positional arguments:
  ENV_DIR               A directory to create the environment in.

optional arguments:
  -h, --help            show this help message and exit
  --system-site-packages
                        Give the virtual environment access to the system site-packages dir.
  --symlinks            Try to use symlinks rather than copies, when symlinks are not the default for
                        the platform.
  --copies              Try to use copies rather than symlinks, even when symlinks are the default for
                        the platform.
  --clear               Delete the contents of the environment directory if it already exists, before
                        environment creation.
  --upgrade             Upgrade the environment directory to use this version of Python, assuming
                        Python has been upgraded in-place.
  --without-pip         Skips installing or upgrading pip in the virtual environment (pip is
                        bootstrapped by default)
  --prompt PROMPT       Provides an alternative prompt prefix for this environment.

Once an environment has been created, you may wish to activate it, e.g. by sourcing an activate script
in its bin directory.
```

参数解析：

- `--system-site-packages` - 在虚拟环境中安装第三方模块时，是否也在系统环境中安装
- `--symlinks` - 使用链接的方式，软链系统环境的Python解释器。默认情况下使用软链的方式
- `--copies` - 使用拷贝的方式，拷贝系统的Python解释器作为虚拟环境的解释器

    ```shell
    # python3 -m venv --symlinks /usr/local/python_env/3.8.6/alfons                     
    # tree ./alfons/bin                               
    ./alfons/bin
    ├── Activate.ps1
    ├── activate
    ├── activate.csh
    ├── activate.fish
    ├── easy_install
    ├── easy_install-3.8
    ├── pip
    ├── pip3
    ├── pip3.8
    ├── python -> python3
    └── python3 -> /usr/local/bin/python3

    0 directories, 11 files

    # python3 -m venv --copies /usr/local/python_env/3.8.6/alfons_copy  
    # tree ./alfons_copy/bin                                      
    ./alfons_copy/bin
    ├── Activate.ps1
    ├── activate
    ├── activate.csh
    ├── activate.fish
    ├── easy_install
    ├── easy_install-3.8
    ├── pip
    ├── pip3
    ├── pip3.8
    ├── python
    └── python3

    0 directories, 11 files
    ```

- `--clear` - 在创建虚拟环境前清理已经存在的目录，不能与 `--upgrade` 一同使用
- `--upgrade` - 升级环境中已经存在的内容，不能与 `--clear` 一同使用
  
    ```shell
    # ll alfons                                                    
    total 0
    -rw-r--r--  1 alfons  wheel     0B  1 12 20:17 ok
    # python3 -m venv --upgrade /usr/local/python_env/3.8.6/alfons                        
    # ll alfons                                        
    total 8
    drwxr-xr-x  9 alfons  wheel   288B  1 12 20:17 bin
    drwxr-xr-x  2 alfons  wheel    64B  1 12 20:17 include
    drwxr-xr-x  3 alfons  wheel    96B  1 12 20:17 lib
    -rw-r--r--  1 alfons  wheel     0B  1 12 20:17 ok
    -rw-r--r--  1 alfons  wheel    75B  1 12 20:17 pyvenv.cfg
    # python3 -m venv --clear /usr/local/python_env/3.8.6/alfons                          
    # ll alfons                                       
    total 8
    drwxr-xr-x  13 alfons  wheel   416B  1 12 20:18 bin
    drwxr-xr-x   2 alfons  wheel    64B  1 12 20:18 include
    drwxr-xr-x   3 alfons  wheel    96B  1 12 20:18 lib
    -rw-r--r--   1 alfons  wheel    75B  1 12 20:18 pyvenv.cfg
    ```

- `--without-pip` - 不在虚拟环境中安装pip

    ```shell
    # python3 -m venv --without-pip /usr/local/python_env/3.8.6/alfons 
    # tree ./alfons/bin    
    ./alfons/bin
    ├── Activate.ps1
    ├── activate
    ├── activate.csh
    ├── activate.fish
    ├── python -> python3
    └── python3 -> /usr/local/bin/python3
    ```

- `--prompt PROMPT` - 指定运行虚拟环境的前缀提示，默认情况下，提示为环境路径

    ```shell
    # python3 -m venv  alfons_no
    # source alfons_no/bin/activate
    (alfons_no) #

    # python3 -m venv --prompt nihao alfons
    # source alfons/bin/activate
    (nihao) #
    ```

### Python虚拟环境与系统环境产生隔离的原理

Python虚拟环境的关键在于 `activate` 文件，里面 **初始化了虚拟环境运行时的环境变量**，指定了 **Python解释器的搜索路径 `PATH`**。

```txt
...
VIRTUAL_ENV="/usr/local/python_env/3.8.6/alfons"
export VIRTUAL_ENV

_OLD_VIRTUAL_PATH="$PATH"
PATH="$VIRTUAL_ENV/bin:$PATH"       // source activate 后，优先从 /usr/local/python_env/3.8.6/alfons/bin/ 目录下找 Python
export PATH
...
```

同时，activate 文件中也可以通过控制环境变量 `PYTHONHOME`、`PYTHONPATH` 来重新定义Python运行时模块搜索路径。

- **PYTHONHOME** - 指定Python标准库路径(`/usr/local/python_env/3.8.6/main/lib/python3.8/`)
- **PYTHONPATH** - 指定Python模块搜索路径(`/usr/local/python_env/3.8.6/alfons/lib/python3.8/site-packages/`)

```shell
# python3
Python 3.8.6 (default, Nov 23 2020, 19:49:30)
[GCC 4.8.5 20150623 (Red Hat 4.8.5-28)] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import sys
>>> import pprint
>>> pprint.pprint(sys.path)
['',
 '/usr/local/lib/python38.zip',
 '/usr/local/lib/python3.8',
 '/usr/local/lib/python3.8/lib-dynload',
 '/usr/local/lib/python3.8/site-packages']      # 主环境的第三方库搜索路径
>>>

(alfons)# python3
Python 3.8.6 (default, Nov 23 2020, 19:49:30)
[GCC 4.8.5 20150623 (Red Hat 4.8.5-28)] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import sys
>>> import pprint
>>> pprint.pprint(sys.path)
['',
 '/usr/local/lib/python38.zip',
 '/usr/local/lib/python3.8',
 '/usr/local/lib/python3.8/lib-dynload',
 '/usr/local/python_env/3.8.6/alfons/lib/python3.8/site-packages']       # 虚拟环境的第三方库搜索路径
>>>
```

虚拟环境中使用的Python模块搜索路径优先排序如下：

- **/usr/local/lib/python3.8** - 系统标准库搜索路径，该路径下保存了标准库文件
- **/usr/local/lib/python3.8/lib-dynload** - 保存模块用到的动态库，Python有些模块使用c语言编写
- **/usr/local/lib/python3.8/site-packages** - 系统环境保存第三方库的路径
- **/usr/local/python_env/3.8.6/alfons/lib/python3.8/site-packages** - `虚拟环境`保存第三方库的路径

```shell
# ls /usr/local/lib/python3.8/
abc.py          _collections_abc.py          distutils           heapq.py      _markupbase.py     poplib.py       selectors.py      _strptime.py                               trace.py
aifc.py         colorsys.py                  doctest.py          hmac.py       mimetypes.py       posixpath.py    shelve.py         struct.py                                  tty.py
...

# ls /usr/local/python_env/3.8.6/alfons/lib/python3.8/
site-packages
```

可以看到，即使我们使用的是Python虚拟环境，但是仍然依赖了系统Python主环境的模块。

通过上面的现象，我们可以得出一个结论：

> Python虚拟环境的制作是为了满足 **本地系统环境中的Python三方库不受污染，而不是为了迁移到其他机器也能使用。**

下面是直接迁移Python虚拟环境(直接拷贝 `/usr/local/python_env/3.8.6/alfons` 下所有文件至安装机器上)的现象，提示系统模块未找到：

```shell
#source bin/activate
(alfons)# python3
Could not find platform independent libraries <prefix>
Could not find platform dependent libraries <exec_prefix>
Consider setting $PYTHONHOME to <prefix>[:<exec_prefix>]
Python path configuration:
  PYTHONHOME = (not set)
  PYTHONPATH = (not set)
  program name = 'python3'
  isolated = 0
  environment = 1
  user site = 1
  import site = 1
  sys._base_executable = '/usr/local/python_env/3.8.6/alfons/bin/python3'
  sys.base_prefix = '/usr/local'
  sys.base_exec_prefix = '/usr/local'
  sys.executable = '/usr/local/python_env/3.8.6/alfons/bin/python3'
  sys.prefix = '/usr/local'
  sys.exec_prefix = '/usr/local'
  sys.path = [
    '/usr/local/lib/python38.zip',
    '/usr/local/lib/python3.8',
    '/usr/local/lib/lib-dynload',
  ]
Fatal Python error: init_fs_encoding: failed to get the Python codec of the filesystem encoding
Python runtime state: core initialized
ModuleNotFoundError: No module named 'encodings'

Current thread 0x00007fa93f09f740 (most recent call first):
<no Python frame>
```

原因就是我们没有同时迁移 `/usr/local/lib/python3.8` 目录下的主环境

## 进击 - 如何创建一个不依赖系统环境的Python虚拟环境?

想要创建一个不依赖系统Python环境的虚拟环境，那就需要 **同时迁移系统环境和虚拟环境**。具体步骤如下：

- 下载Python源码，编译安装Python
  - 指定Python主环境的安装路径，默认情况下为 `/usr/local/bin/python`
  - 编译配置时，使用 `--prefix` 参数指定安装路径
  - 编译主环境
  - 安装主环境

  ```shell
  # tar -xf Python-3.8.6.tgz 
  # cd Python-3.8.6
  # ./configure --prefix=/usr/local/python_env/3.8.6/main  --disable-option-checking --enable-shared  --enable-loadable-sqlite-extensions 
  # make -j "$(nproc)" 
  # make install
  ```

- 制作虚拟环境

  ```shell
  # export LD_LIBRARY_PATH=/usr/local/python_env/3.8.6/main/lib:$LD_LIBRARY_PATH 
  # /usr/local/python_env/3.8.6/main/bin/python3 -m venv  --symlinks --prompt alfons /usr/local/python_env/3.8.6/alfons
  ```

- 在 **activate** 文件中添加动态库搜索路径 `LD_LIBRARY_PATH`
  
  ```shell
  # echo "export LD_LIBRARY_PATH=/usr/local/python_env/3.8.6/main/lib:$LD_LIBRARY_PATH" >> /usr/local/python_env/3.8.6/alfons/bin/activate
  ```

- 打包 Python主环境 和 虚拟环境

但是，将 Python主环境 和 虚拟环境 通过这种方式部署后，仍然会出现其他的问题：**动态库(*.so)找不到**。

### 解决Python虚拟环境 *.so 依赖问题

首先在解决这个问题之前，我们要明确一点：**Linux 中，不管是静态链接还是动态加载，在运行时，所依赖的库文件的搜索路径都是按照一定顺序来查找的**

- 「1」编译目标代码时指定的动态库搜索路径 **rpath**，编译过程中指定
- 「2」环境变量 **LD_LIBRARY_PATH** 指定的动态库搜索路径，运行时指定
- 「3」配置文件 **/etc/ld.so.conf** 中指定的动态库搜索路径
- 「4」默认的动态库搜索路径 **/lib**
- 「5」默认的动态库搜索路径 **/usr/lib**

#### ~~「不能解决问题」方法一：拷贝系统动态库，改变LD_LIBRARY_PATH~~

- 查询标准库so文件依赖的系统动态库路径
- 将依赖的系统动态库路径拷贝至 `/usr/local/python_env/system_lib` 下
- 修改虚拟环境中的 `LD_LIBRARY_PATH` 参数，按照下面的顺序进行查找
  - `/usr/local/python_env/3.8.6/main/lib` - 查找 `libpython.so`
  - `/lib、/lib64、/usr/lib` - 系统动态库路径
  - `/usr/local/python_env/system_lib` - 拷贝的系统动态库路径

解决思路是，虚拟环境会 **先在系统中查找动态库**，如果没有找到，**转至拷贝的系统动态库路径进行查找**。

这种方式可能会有不足之处，新打好的包，可能会出现 **glibc** 版本不兼容的情况。原因在于，编译环境中的 **glibc版本和运行环境中的glibc版本** 不一样。

```shell
#source /usr/local/python_env/3.8.6/alfons/bin/activate
(alfons)#python3
python3: /lib64/libc.so.6: version `GLIBC_2.15' not found (required by /usr/local/python_env/3.8.6/main/lib/libpython3.8d.so.1.0)
python3: /lib64/libc.so.6: version `GLIBC_2.14' not found (required by /usr/local/python_env/3.8.6/main/lib/libpython3.8d.so.1.0)
python3: /lib64/libc.so.6: version `GLIBC_2.17' not found (required by /usr/local/python_env/3.8.6/main/lib/libpython3.8d.so.1.0)

#strings /lib64/libc.so.6 | grep GLIBC
GLIBC_2.2.5
GLIBC_2.2.6
GLIBC_2.3
GLIBC_2.3.2
GLIBC_2.3.3
GLIBC_2.3.4
GLIBC_2.4
GLIBC_2.5
GLIBC_2.6
GLIBC_2.7
GLIBC_2.8
GLIBC_2.9
GLIBC_2.10
GLIBC_2.11
GLIBC_2.12
GLIBC_PRIVATE
```

> 为什么不先在 **拷贝的系统动态库路径进行查找**？
> 按照下面的顺序进行查找
>  - `/usr/local/python_env/3.8.6/main/lib` - 查找 `libpython.so`
>  - `/usr/local/python_env/system_lib` - 拷贝的系统动态库路径
>  - `/lib、/lib64、/usr/lib` - 系统动态库路径
>
> 如果设置 **拷贝的系统动态库路径** 优先，会出现 在Python代码中，如果需要运行系统命令，由于设置的 **LD_LIBRARY_PATH** 环境变量关系，系统命令对应的依赖，首先从 **拷贝的系统动态库路径** 查找，仍然会出现 glic 版本不一致的问题

#### 方法二：修改环境中可执行程序和依赖动态库的 RUNPATH（rpath）

使用 [patchelf](https://github.com/NixOS/patchelf) 修改编译后的动态库或可执行程序的 `RUNPATH` 和 `ld-linux.so` 程序的路径。

- 修改动态库的 `runpath` - `patchelf --set-rpath {new_rpath} {so}`
- 修改动态库的 `ld-linux.so` 链接器路径 - `patchelf --set-interpreter {new_ld_so_path} {so}`

通过此方法修改后，动态库首先会在 `rpath` 路径下查找指定的动态库，就不牵扯到 LD_LIBRARY_PATH 环境变量的问题。

```shell
# ldd /usr/local/python_env/3.8.6/alfons/main/lib/libpython3.8.so.1.0
	linux-vdso.so.1 =>  (0x00007ffcf1ffe000)
	libcrypt.so.1 => /usr/local/python_env/system_lib/alfons/libcrypt.so.1 (0x00007f7489323000)
	libpthread.so.0 => /usr/local/python_env/system_lib/alfons/libpthread.so.0 (0x00007f7489103000)
	libdl.so.2 => /usr/local/python_env/system_lib/alfons/libdl.so.2 (0x00007f7488efe000)
	libutil.so.1 => /usr/local/python_env/system_lib/alfons/libutil.so.1 (0x00007f7488cfa000)
	libm.so.6 => /usr/local/python_env/system_lib/alfons/libm.so.6 (0x00007f74889f5000)
	libc.so.6 => /usr/local/python_env/system_lib/alfons/libc.so.6 (0x00007f748861c000)
	libfreebl3.so => /usr/local/python_env/system_lib/alfons/libfreebl3.so (0x00007f7488418000)
	/lib64/ld-linux-x86-64.so.2 (0x00007f7489b06000)
```

## 后记：如何减小虚拟环境体积？

制作后的 **虚拟环境+主环境** 体积有 `203M`，主环境便有 `189M`！由于已经使用了动态库、链接的方式，在Python解释器上已经没有过多的操作空间。

```shell
# tree ./alfons/bin/
./alfons/bin/
├── activate
├── activate.csh
├── activate.fish
├── Activate.ps1
├── easy_install
├── easy_install-3.8
├── pip
├── pip3
├── pip3.8
├── python -> python3
└── python3 -> /usr/local/python_env/3.8.6/main/bin/python3

# du -h --max-depth=1 ./
189M	./main
14M	./alfons
203M	./
```

查看后，发现主环境中有许多的 **测试代码**、**exe文件**、**doc文件**，这些文件对于Linux运行环境来说是非必要的，可以去除。

```shell
# find /usr/local/python_env/3.8.6/ -type d -name test -o -name tests -o -name idle_test -o -name test-data -o -name __pycache__ | xargs rm -rf 
# find /usr/local/python_env/3.8.6/ -type f -name *.exe -o -name *.pyc -o -name *.pyi | xargs rm -rf 
# rm -rf /usr/local/python_env/3.8.6/main/share
#du -h --max-depth=1 ./
81M	./main
7.4M	./alfons
89M	./
```

删减掉这些不必要的文件后，**虚拟环境 + 主环境** 体积 `89M`。

## 总结

- Python虚拟环境，主要的目的是解决 **项目环境和系统环境隔离**，**而不是以迁移至其他主机为目的**。
- Python虚拟环境的主要实现原理是，**通过 `activate文件` 重新定义运行时环境变量**。
- Python3开始，主要使用系统自带的 `venv` 模块进行虚拟环境的制作。
- 通过 修改可执行程序和依赖的动态库 的rpath，可以使虚拟环境完全独立于操作系统
- 主环境中的 **测试文件**、**doc文件** 可以去除，不影响程序运行。

## 参考

- [patchelf](https://github.com/NixOS/patchelf)
