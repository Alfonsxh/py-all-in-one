#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import platform
import shutil
import abc
import time
import argparse
import functools

root_dir = os.path.dirname(__file__)  # /packages
root_dir = root_dir if root_dir.strip() else "/packages"
python_package_dir = os.path.join(root_dir, "Python")  # /packages/Python/
install_script_template = os.path.join(root_dir, "install.sh")  # /packages/install.sh
requirements_path = os.path.join(root_dir, "requirements.txt")  # /packages/requirements.txt
patchelf_path = os.path.join(root_dir, "patchelf")  # /packages/patchelf

default_python_prefix = "/root/.python_env"  # python环境安装的默认路径


# ========================== 打印 ===============================
class Printer:

    def __init__(self):
        pass

    def print_title(self, title, width=64, fill_chr='+', is_end=False):
        self.print_white(msg='\033[92m{0}\033[0m{1}'.format(title.center(width, fill_chr),
                                                            "\n" if is_end else ""))

    def print_ok(self, ok_msg):
        self.print_white(msg='\033[92m[ OK ]\033[0m: ' + str(ok_msg))

    def print_warning(self, warn_msg):
        self.print_white(msg='\033[93m[ WARNING ]\033[0m: ' + str(warn_msg))

    def print_error(self, error_msg):
        self.print_white(msg='\033[91m[ ERROR ]\033[0m: ' + str(error_msg))

    @staticmethod
    def print_white(msg):
        print(msg)

    def exit(self, exit_code, error_msg=None):
        if error_msg:
            self.print_error(error_msg=error_msg)
        sys.exit(exit_code)

    @staticmethod
    def confirm(prompt_msg):
        input_str = raw_input('\033[93m{0}\033[0m [y/n]: '.format(prompt_msg))
        if input_str.lower() not in ['y', 'yes']:
            sys.exit(0)


printer = Printer()


# ================================= 执行命令相关 ===============================
def run_local_cmd(cmd, raise_when_error=True):
    """
    执行本地命令
    :param cmd: 待执行的命令
    :param raise_when_error: 错误时raise
    :return:
    """
    printer.print_ok(ok_msg="Execute cmd -> {cmd}".format(cmd=cmd))
    res = os.system(cmd)
    if raise_when_error and res != 0:
        raise


def get_python_version():
    """
    获取支持的python版本列表
    """
    python_version_list = list()
    for python_package in os.listdir(python_package_dir):
        python_version_list.append(python_package[python_package.find('-') + 1: python_package.rfind('.tgz')])

    return python_version_list


def rate_log_wrapper(title):
    def wrapper_func(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            printer.print_title(title=title)
            time.sleep(1)
            res = func(*args, **kwargs)
            printer.print_ok(ok_msg="{title}[成功]！\n".format(title=title))

            return res

        return wrapper

    return wrapper_func


# ================================= builder 对象 ===============================
class PythonBuildBase:
    def __init__(
        self,
        install_prefix,
        python_version,
        project,
        prompt,
    ):
        """
        Python安装基类
        :param install_prefix: 配置的python sys.path 查找的根目录
        :param python_version: Python环境
        :param project: 项目名称
        :param prompt: 虚拟环境进入提示
        """
        self.install_prefix = install_prefix
        self.python_version = python_version
        self.project = project
        self.prompt = prompt

        # patchelf 程序路径
        self.patchelf_path = patchelf_path
        run_local_cmd("chmod +x {patchelf_path}".format(patchelf_path=self.patchelf_path))

        # Python安装包路径
        self._python_package_path = os.path.join(python_package_dir, "Python-{version}.tgz".format(version=python_version))

        # 系统动态库依赖路径
        self._system_ld_load_path = os.path.join(install_prefix, "system_lib", self.project)  # {default_python_prefix}/system_lib/{project_name}
        if not os.path.isdir(self._system_ld_load_path):
            os.makedirs(self._system_ld_load_path)

        if platform.machine() == "aarch64":
            self._ld_linux_path_src = "/lib64/ld-linux-aarch64.so.1"
        else:
            self._ld_linux_path_src = "/lib64/ld-linux-x86-64.so.2"
        self._ld_linux_path_dst = os.path.join(self._system_ld_load_path, os.path.basename(self._ld_linux_path_src))

        # 安装环境路径
        self._env_root_dir = os.path.join(install_prefix, python_version)  # {default_python_prefix}/3.8.6/

        # Python虚拟环境安装路径
        self._env_virtual_dir = os.path.join(self._env_root_dir, project)  # {default_python_prefix}/3.8.6/{project}

        # Python主环境安装路径
        self._env_main_dir = os.path.join(self._env_virtual_dir, "main")  # {default_python_prefix}/3.8.6/{project}/main
        self._main_ld_load_path = os.path.join(self._env_main_dir, "lib")  # {default_python_prefix}/3.8.6/{project}/main/lib/libpython3.8d.so

        # 打包相关参数
        self._build_dir = os.path.join(root_dir, "build")  # 包存放路径
        self._tar_dir = os.path.join(self._build_dir, project)  # tar包存放路径
        if not os.path.isdir(self._tar_dir):
            os.makedirs(self._tar_dir)

        self._virtual_archive_path = os.path.join(self._tar_dir, "{project}_env_virtual.tar.gz".format(project=project))  # /packages/build/{project}/{project}_env_virtual.tar.gz
        self._system_lib_archive_path = os.path.join(self._tar_dir, "system_lib.tar.gz")  # /packages/build/{project}/"system_lib.tar.gz"
        self._install_script_path = os.path.join(self._tar_dir, "install.sh")  # /packages/build/{project}/install.sh

        self._python_package_tar = os.path.join(self._build_dir,
                                                "{project}_{arch}_env.tar.gz".format(project=project, arch=platform.machine()))  # /packages/build/{project}_{arch}_env.tar.gz

    # ========================= Python环境 =========================
    @rate_log_wrapper(title="编译安装Python主环境")
    def build_main_env(self):
        """
        编译安装Python系统环境
        """
        printer.print_white("Python配置的prefix -> {prefix}".format(prefix=self._env_main_dir))

        run_local_cmd(cmd="export PATH={install_dir}/bin:$PATH "
                          "&& cd {package_dir} "
                          "&& tar -xf Python-{version}.tgz -C /tmp/"
                          "&& cd /tmp/Python-{version} "
        # 在x86环境中 --with-pydebug 参数可能导致异常
        # "&& ./configure --prefix={install_dir} --disable-option-checking --with-pydebug --enable-shared --enable-loadable-sqlite-extensions "
                          "&& ./configure --prefix={install_dir} --disable-option-checking --enable-shared --enable-loadable-sqlite-extensions "
                          "&& make -j \"$(nproc)\" "
                          "&& make install"
                          "".format(install_dir=self._env_main_dir,
                                    package_dir=python_package_dir,
                                    version=self.python_version))

        if not os.path.isdir(self._env_main_dir):
            printer.exit(exit_code=1, error_msg="编译安装Python主环境失败!")

    @abc.abstractmethod
    def build_virtual_env(self):
        """
        制作虚拟环境
        """
        pass

    @rate_log_wrapper(title="安装项目第三方依赖包")
    def pip_install(self):
        """
        安装项目第三方依赖包
        """
        if not os.path.isfile(requirements_path):
            printer.print_ok(ok_msg="{requirements}不存在，跳过第三方依赖包安装".format(requirements=requirements_path))
            return

        run_local_cmd("source {virtual_env_dir}/bin/activate "
                      "&& export LD_LIBRARY_PATH={ld_library_path}:$LD_LIBRARY_PATH "
                      "&& pip install --upgrade pip "
                      "&& pip install -r {requirements} "
                      "".format(virtual_env_dir=self._env_virtual_dir,
                                ld_library_path=self._main_ld_load_path,
                                requirements=requirements_path))

    # ======================= 系统动态库相关 =======================
    @rate_log_wrapper(title="拷贝环境依赖的所有动态库")
    def pack_library(self):
        """
        查询环境中可执行文件依赖的所有动态库
        """
        tmp_lds_path = "/tmp/system_lds"

        # 找到环境中所有的动态库依赖
        run_local_cmd(cmd="find %s -name '*.so' "
                          "| xargs ldd 2>/dev/null "
                          "| grep = "
                          "| grep -v libpython "
                          "| awk -F\\( '{print $1}' "
                          "| sort | uniq "
                          "| awk  '{print $3}' > %s" % (self._env_root_dir, tmp_lds_path))

        with open(tmp_lds_path, "a") as f:
            f.write(self._ld_linux_path_src)

        with open(tmp_lds_path, 'r') as f:
            for system_so_path in f.readlines():
                # 原始动态库依赖地址 /lib64/libc.so.6
                system_so_path = system_so_path.strip()
                if not system_so_path:
                    continue

                # 如果属于链接，需要查询其真实路径，如 /lib64/libc.so.6 -> libc.so.6.1
                dir_name = os.path.dirname(system_so_path)
                if os.path.islink(system_so_path):
                    real_path = os.path.join(dir_name, os.readlink(system_so_path))
                else:
                    real_path = system_so_path

                # 格式化拷贝动态库的原始路径和目标路径
                src_file = real_path
                dst_file = "{system_lib_path}/{lib_name}".format(system_lib_path=self._system_ld_load_path, lib_name=os.path.basename(system_so_path))
                shutil.copyfile(src=src_file, dst=dst_file)
                shutil.copymode(src=src_file, dst=dst_file)

                printer.print_ok("拷贝动态库 {src_file} -> {dst_file} 成功！".format(src_file=src_file, dst_file=dst_file))

    def _patchelf_operator(
        self,
        elf_path,
        runpath_switch=True,
        runpath_switch_path=None,
        ld_switch=True,
    ):
        """
        使用 patchelf 修改 elf 文件导入
        :param elf_path: elf文件路径
        :param runpath_switch: 修改runpath
        :param runpath_switch_path: 需要添加的 runpath 路径
        :param ld_switch: 修改ld-linux
        :return:
        """
        # 修改动态库的 rpath 和 ld-linux-x86-64.so.2 入口
        if runpath_switch:
            if not runpath_switch_path:
                runpath_switch_path = [self._system_ld_load_path]

            run_local_cmd(
                cmd="{patchelf} --set-rpath {rpath} {system_so}".format(patchelf=self.patchelf_path, rpath=":".join(runpath_switch_path), system_so=elf_path),
                raise_when_error=False,
            )

            printer.print_ok(ok_msg="{elf_path} change rpath -> {rpath}\n".format(elf_path=elf_path, rpath=":".join(runpath_switch_path)))

        if ld_switch:
            run_local_cmd(
                cmd="{patchelf} --set-interpreter {ld_so} {system_so}".format(patchelf=self.patchelf_path, ld_so=self._ld_linux_path_dst, system_so=elf_path),
                raise_when_error=False,
            )

            printer.print_ok(ok_msg="{elf_path} change interpreter -> {ld_linux}\n".format(elf_path=elf_path, ld_linux=self._ld_linux_path_dst))

    @staticmethod
    def _is_elf_file(file_path):
        """
        判断是否为elf文件
        :param file_path: 文件路径
        :return:
        """
        if os.path.islink(file_path):
            return False

        if os.path.isdir(file_path):
            return False

        with open(file_path, 'rb') as f:
            elf_ident = f.read(4)
            magic = [ord(i) for i in elf_ident]
            if magic[0] != 127 or magic[1] != ord('E') or magic[2] != ord('L') or magic[3] != ord('F'):
                return False
            else:
                return True

    @rate_log_wrapper(title="修改动态库RUNPATH")
    def change_elf_property(self):
        """
        使用 patchelf 修改动态库导入
        """
        tmp_env_lds_path = "/tmp/env_lds"

        # 找到环境中所有的动态库依赖
        run_local_cmd(cmd="find %s -name '*.so*' > %s" % (os.path.dirname(self._env_root_dir), tmp_env_lds_path))

        with open(tmp_env_lds_path, 'r') as f:
            for system_so_path in f.readlines():
                # 原始动态库依赖地址 /lib64/libc.so.6
                system_so_path = system_so_path.strip()
                if not system_so_path:
                    continue

                # 动态库修改
                if not os.path.isfile(system_so_path) \
                    or self._ld_linux_path_dst == system_so_path:  # 不修改 ld-linux的链接程序
                    continue

                self._patchelf_operator(elf_path=system_so_path)

        # 解释器修改
        for python_bin_dir in ["{main_dir}/bin".format(main_dir=self._env_main_dir), "{virtual_dir}/bin".format(virtual_dir=self._env_virtual_dir)]:
            for python_exe in os.listdir(python_bin_dir):
                if python_exe.startswith("python"):
                    self._patchelf_operator(elf_path=os.path.join(python_bin_dir, python_exe), runpath_switch_path=[self._main_ld_load_path, self._system_ld_load_path])

        # 解释器修改
        third_bin_dir = "{virtual_env_dir}/bin".format(virtual_env_dir=self._env_virtual_dir)
        for third_bin in os.listdir(third_bin_dir):
            third_bin_path = os.path.join(third_bin_dir, third_bin)
            if self._is_elf_file(file_path=third_bin_path):
                self._patchelf_operator(elf_path=os.path.join(third_bin_dir, third_bin_path), runpath_switch_path=[self._main_ld_load_path, self._system_ld_load_path])

    # ======================= 清理多余的内容 =======================
    @rate_log_wrapper(title="清理安装后的环境")
    def clean(self):
        """
        全部完成后，清理环境，清除多余的文件
        """
        run_local_cmd("find {env_dir} -type d -name test -o -name tests -o -name idle_test -o -name test-data -o -name __pycache__ "
                      "| xargs rm -rf "
                      "".format(env_dir=self._env_root_dir))

        run_local_cmd("find {env_dir} -type f -name *.exe -o -name *.pyc -o -name *.pyi"
                      "| xargs rm -rf "
                      "".format(env_dir=self._env_root_dir))

        run_local_cmd("rm -rf {main_env}/share".format(main_env=self._env_main_dir))

    # ======================= 打包 =======================
    @rate_log_wrapper(title="打包环境")
    def archive(self):
        """
        打包环境
        """
        # 环境打包
        run_local_cmd("tar -czf {archive_name} {target_dir}"
                      "".format(archive_name=self._virtual_archive_path,
                                target_dir=self._env_virtual_dir))
        run_local_cmd("tar -czf {archive_name} {target_dir}"
                      "".format(archive_name=self._system_lib_archive_path,
                                target_dir=self._system_ld_load_path))

        # 制作安装脚本
        with open(install_script_template, "r") as f_template:
            install_plaintext = f_template.read()
            install_plaintext = install_plaintext.replace("__virtual_env_package__", os.path.basename(self._virtual_archive_path))
            install_plaintext = install_plaintext.replace("__system_lib_package__", os.path.basename(self._system_lib_archive_path))
            install_plaintext = install_plaintext.replace("__virtual_env_active__", self._env_virtual_dir)

            with open(self._install_script_path, "w") as f:
                f.write(install_plaintext)

        # 环境安装包打包
        run_local_cmd(
            "cd {build_dir} "
            "&& tar -czf {package_tar} {tar_dir}"
            "".format(
                build_dir=self._build_dir,
                package_tar=os.path.basename(self._python_package_tar),
                tar_dir=os.path.basename(self._tar_dir),
            ))

        # 清理临时文件
        run_local_cmd("rm -rf {tar_dir}".format(tar_dir=self._tar_dir))

    @rate_log_wrapper(title="打包")
    def run(self):
        # 安装Python主环境
        self.build_main_env()

        # 制作虚拟环境相关
        self.build_virtual_env()
        self.pip_install()

        # 打包环境依赖的系统动态库
        self.pack_library()
        self.change_elf_property()

        # 环境清理
        self.clean()

        # 打包环境
        self.archive()

        printer.print_ok("包位置：{package_file}".format(package_file=self._python_package_tar))


class Python2Build(PythonBuildBase):

    @rate_log_wrapper(title="制作虚拟环境")
    def build_virtual_env(self):
        """
        制作虚拟环境
        """
        # 制作python2虚拟环境时，链接目标版本Python的主环境动态库、冲重定义
        run_local_cmd(
            "export LD_LIBRARY_PATH={LD_LIBRARY_PATH}:$LD_LIBRARY_PATH "
            "&& export PYTHONPATH=/usr/lib/python2.7/site-packages/ "
            "&& {main_dir}/bin/python{version} -m pip install virtualenv "
            "&& {main_dir}/bin/python{version} -m virtualenv --prompt={prompt} {virtual_dir}"
            "".format(
                main_dir=self._env_main_dir,
                version=self.python_version[0],
                prompt=self.prompt,
                virtual_dir=self._env_virtual_dir,
                LD_LIBRARY_PATH=self._main_ld_load_path,
            ))


class Python3Build(PythonBuildBase):

    @rate_log_wrapper(title="制作虚拟环境")
    def build_virtual_env(self):
        """
        制作虚拟环境
        :return:
        """
        run_local_cmd(
            "export LD_LIBRARY_PATH={LD_LIBRARY_PATH}:$LD_LIBRARY_PATH "
            "&& {main_dir}/bin/python{version} -m venv --symlinks --prompt {prompt} {virtual_dir}"
            "".format(
                main_dir=self._env_main_dir,
                version=self.python_version[0],
                prompt=self.prompt,
                virtual_dir=self._env_virtual_dir,
                LD_LIBRARY_PATH=self._main_ld_load_path,
            ))


def get_args(args):
    parser = argparse.ArgumentParser(
        description="此脚本用于制作Python项目的虚拟环境，支持的Python版本如下：{version}"
                    "".format(version="\n\t- ".join([""] + get_python_version())),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--install-dir",
        help="指定环境的路径, 默认的环境路径为: {default}"
             "".format(default=default_python_prefix),
        required=False,
        default=default_python_prefix,
        action="store",
        dest="prefix",
    )

    parser.add_argument(
        "--project",
        help="指定项目的名字",
        required=True,
        action="store",
        dest="project",
    )

    parser.add_argument(
        "--python-version",
        help="指定python的版本",
        required=True,
        choices=get_python_version(),
        action="store",
        dest="py_version",
    )

    if args:
        return parser.parse_args(args=args)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == '__main__':

    args = get_args(sys.argv[1:])

    if args.py_version.startswith('3'):
        Python3Build(
            install_prefix=args.prefix,
            python_version=args.py_version,
            project=args.project,
            prompt=args.project,
        ).run()
    elif args.py_version.startswith('2'):
        Python2Build(
            install_prefix=args.prefix,
            python_version=args.py_version,
            project=args.project,
            prompt=args.project,
        ).run()
    else:
        printer.exit(
            exit_code=1,
            error_msg="暂不支持该版本({version})的安装！请先准备Python源码包在{python_package_dir}下!".format(version=args.py_version, python_package_dir=python_package_dir),
        )
