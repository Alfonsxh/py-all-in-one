#!/bin/bash

# Install dynamic library dependencies
/bin/tar -xzf "__system_lib_package__" -C /

# Install virtual environment
/bin/tar -xzf "__virtual_env_package__" -C /

echo "use: source __virtual_env_active__/bin/activate"