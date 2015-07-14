#!/bin/bash
set -ex

python .build/download_dependencies.py

if [ ! -e .build/squeak ]; then
    wget http://squeakvm.org/unix/release/Squeak-4.10.2.2614-linux_i386.tar.gz
    tar xzvf Squeak-4.10*.tar.gz
    rm Squeak-4.10*.tar.gz
    ln -s $PWD/Squeak-4.10*/bin/squeak .build/squeak
fi

.travis/setup_arm.sh
