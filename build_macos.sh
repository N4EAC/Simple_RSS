#!/bin/zsh
set -euo pipefail

cd "${0:A:h}"

app_name="Simple RSS"
app_version="1.5"
icon_file="build/SimpleRSS.icns"
dmg_file="dist/Simple_RSS_${app_version}_macOS.dmg"
staging_dir="$(mktemp -d)"
trap 'rm -rf "$staging_dir"' EXIT

python3 -m pip install -r requirements-build.txt

mkdir -p build
python3 -c 'from PIL import Image; image = Image.open("simple_rss.png"); image.save("build/SimpleRSS.icns", format="ICNS", sizes=[(16, 16), (32, 32), (64, 64), (128, 128), (256, 256), (512, 512), (1024, 1024)])'

python3 -m PyInstaller --noconfirm --clean --windowed \
  --name "$app_name" \
  --icon "$icon_file" \
  --osx-bundle-identifier "com.eduardo.simple-rss" \
  --add-data "simple_rss.png:." \
  simple_rss.py

app_bundle="dist/${app_name}.app"
plutil -replace CFBundleShortVersionString -string "$app_version" \
  "${app_bundle}/Contents/Info.plist"
plutil -replace CFBundleVersion -string "$app_version" \
  "${app_bundle}/Contents/Info.plist"
codesign --force --deep --sign - "$app_bundle"

cp -R "$app_bundle" "$staging_dir/"
ln -s /Applications "$staging_dir/Applications"
hdiutil create \
  -volname "$app_name" \
  -srcfolder "$staging_dir" \
  -ov -format UDZO \
  "$dmg_file"

print "Built dist/${app_name}.app"
print "Built ${dmg_file}"
