rm -rf debian_pkg
mkdir debian_pkg
mkdir -p debian_pkg/DEBIAN
mkdir -p debian_pkg/usr/bin
mkdir -p debian_pkg/usr/bin/cryptohubminer
cp miner.py debian_pkg/usr/bin/cryptohubminer/miner.py
