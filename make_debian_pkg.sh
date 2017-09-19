rm -rf debian_pkg
mkdir debian_pkg
mkdir -p debian_pkg/DEBIAN
mkdir -p debian_pkg/usr/bin
mkdir -p debian_pkg/usr/bin/cryptohubminer
cp miner.py debian_pkg/usr/bin/cryptohubminer/miner.py
cp start.sh debian_pkg/usr/bin/cryptohubminer_start

touch debian_pkg/DEBIAN/control
echo -e  "Package: cryptohubminer" >> debian_pkg/DEBIAN/control
echo -e  "Version: 0.1" >> debian_pkg/DEBIAN/control
echo -e  "Provides: cryptohubminer" >> debian_pkg/DEBIAN/control
echo -e  "Maintainer: Cryptohub <support@cryptohub.online>" >> debian_pkg/DEBIAN/control
echo -e  "Architecture: amd64" >> debian_pkg/DEBIAN/control
echo -e  "Section: misc" >> debian_pkg/DEBIAN/control
echo -e  "Description: GUI app for mining using ccminer, sgminer and cpuminer." >> debian_pkg/DEBIAN/control

echo -e  "Depends: python3,libgtk-3-dev,python3-pip,libcurl3" >> debian_pkg/DEBIAN/control


mkdir -p debian_pkg/usr/share/applications
cp cryptohubminer.desktop debian_pkg/usr/share/applications/cryptohubminer.desktop
mkdir -p debian_pkg/usr/share
mkdir -p debian_pkg/usr/share/pixmaps
cp imgs/icon.png debian_pkg/usr/share/pixmaps/icon.png
cp -r imgs debian_pkg/usr/bin/cryptohubminer/imgs
cp -r hwinfo debian_pkg/usr/bin/cryptohubminer/hwinfo
chmod 777 -R debian_pkg/usr/bin/cryptohubminer/hwinfo
mkdir debian_pkg/usr/bin/cryptohubminer/cpuminer
cp cpuminer/cpuminer debian_pkg/usr/bin/cryptohubminer/cpuminer/cpuminer
cp cpuminer/libcrypto.so debian_pkg/usr/bin/cryptohubminer/cpuminer/libcrypto.so
mkdir debian_pkg/usr/bin/cryptohubminer/ccminer
cp ccminer/ccminer debian_pkg/usr/bin/cryptohubminer/ccminer/ccminer
cp -R sgminer debian_pkg/usr/bin/cryptohubminer/sgminer

hashdeep -r debian_pkg/usr > debian_pkg/DEBIAN/md5sums

cp postinst debian_pkg/DEBIAN/postinst
chmod 775 debian_pkg/DEBIAN/postinst
