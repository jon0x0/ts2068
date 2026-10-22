#!/bin/sh
# Build downloaded upstream sources locally; installs no emulator system-wide.
set -eu
cd "$(dirname "$0")/.."
root=$(pwd)
prefix="$root/build/analysis/fuse-runtime"
work=/tmp/cpm2068-jlo-build
mkdir -p "$work"
cp -an "$root/build/analysis/libspectrum-source" "$work/"
cp -an "$root/build/analysis/fuse-jlo-source" "$work/"
if [ ! -f "$prefix/lib/pkgconfig/libspectrum.pc" ]; then
cd "$work/libspectrum-source"
sh autogen.sh
./configure --prefix="$prefix" --with-fake-glib --without-libgcrypt --without-zlib --without-bzip2 --with-wav-backend=pcm
make -j4
make install
fi
cd "$work/fuse-jlo-source"
sh autogen.sh
PKG_CONFIG_PATH="$prefix/lib/pkgconfig" ./configure --prefix="$prefix" --with-null-ui --without-gtk --without-x --without-libxml2 --without-png --without-zlib --without-alsa --without-oss --without-pulseaudio --disable-spectranet
make -j4
make install
