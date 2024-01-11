#!/bin/bash

# Install dynamic library dependencies
/bin/tar -xvzf "__system_lib_package__" -C /

# Install virtual environment
/bin/tar -xvzf "__virtual_env_package__" -C /
