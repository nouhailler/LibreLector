#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
DEB_DIR="$SCRIPT_DIR/debian"
LIB_DIR="$DEB_DIR/usr/local/lib/librelector"
VERSION=$(grep '^Version:' "$DEB_DIR/DEBIAN/control" | awk '{print $2}')
ARCH=$(grep '^Architecture:' "$DEB_DIR/DEBIAN/control" | awk '{print $2}')
OUTPUT="$SCRIPT_DIR/librelector_${VERSION}_${ARCH}.deb"

echo "==> Version : $VERSION"

echo "==> Nettoyage du code source précédent..."
rm -rf "$LIB_DIR/librelector"
rm -f "$LIB_DIR/__editable__"*.pth

echo "==> Copie du code source librelector..."
cp -r "$ROOT_DIR/src/librelector" "$LIB_DIR/librelector"

echo "==> Vérification des permissions..."
chmod 755 "$DEB_DIR/DEBIAN/postinst"
chmod 755 "$DEB_DIR/DEBIAN/postrm"
chmod 755 "$DEB_DIR/usr/local/bin/librelector"
chmod 755 "$DEB_DIR/usr/local/lib/librelector/bin/librelector"

echo "==> Construction du paquet .deb..."
dpkg-deb --build --root-owner-group "$DEB_DIR" "$OUTPUT"

echo ""
echo "Paquet créé : $OUTPUT"
echo "Installer avec : sudo dpkg -i $OUTPUT"
