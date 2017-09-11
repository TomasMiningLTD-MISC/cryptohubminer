rm -rf debian_pkg
mkdir debian_pkg
mkdir -p debian_pkg/DEBIAN
mkdir -p debian_pkg/usr/bin
mkdir -p debian_pkg/usr/bin/cryptohubminer
cp miner.py debian_pkg/usr/bin/cryptohubminer/miner.py

touch debian_pkg/DEBIAN/control
echo -e  "Package: cryptohubminer" >> debian_pkg/DEBIAN/control
echo -e  "Version: 0.1" >> debian_pkg/DEBIAN/control}
echo -e  "Provides: cryptohubminer" >> debian_pkg/DEBIAN/control
echo -e  "Maintainer: Cryptohub <support@cryptohub.online>" >> debian_pkg/DEBIAN/control
echo -e  "Architecture: amd64" >> debian_pkg/DEBIAN/control
echo -e  "Section: misc" >> debian_pkg/DEBIAN/control
echo -e  "Depends: python3" >> debian_pkg/DEBIAN/control


mkdir -p debian_pkg/usr/share/applications
cp cryptohubminer.desktop debian_pkg/usr/share/applications/cryptohubminer.desktop
cp imgs/icon.png debian_pkg/usr/share/pixmaps/icon.png

md5deep -r debian_pkg/usr > debian_pkg/DEBIAN/md5sums


touch debian_pkg/DEBIAN/postinst
echo -e  'if [ "$1" = "configure" ] && [ -x "`which update-menus 2>/dev/null`" ] ; then
update-menus
fi' >> debian_pkg/DEBIAN/postinst
