#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

app_name="Simple RSS"
package_name="simple-rss"
app_version="1.5"
install_package=false
skip_dependencies=false

usage() {
  printf '%s\n' \
    "Usage: ./build_linux.sh [--install] [--skip-dependencies]" \
    "" \
    "  --install            Install the completed package after building it." \
    "  --skip-dependencies  Do not install operating-system build dependencies." \
    "  --help               Show this help message."
}

for argument in "$@"; do
  case "$argument" in
    --install) install_package=true ;;
    --skip-dependencies) skip_dependencies=true ;;
    --help|-h) usage; exit 0 ;;
    *) printf 'Unknown option: %s\n\n' "$argument" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ ! -r /etc/os-release ]]; then
  printf 'Unable to detect this Linux distribution: /etc/os-release is missing.\n' >&2
  exit 1
fi

# shellcheck disable=SC1091
source /etc/os-release
distro_id="${ID:-}"
distro_family=" ${ID_LIKE:-} "

if [[ "$distro_id" == "ubuntu" || "$distro_id" == "debian" || "$distro_family" == *" debian "* ]]; then
  package_format="deb"
elif [[ "$distro_id" == "fedora" || "$distro_family" == *" fedora "* || "$distro_family" == *" rhel "* ]]; then
  package_format="rpm"
else
  printf 'Unsupported distribution: %s. Ubuntu/Debian and Fedora-family systems are supported.\n' "${PRETTY_NAME:-$distro_id}" >&2
  exit 1
fi

run_as_root() {
  if [[ "$(id -u)" -eq 0 ]]; then
    "$@"
  elif command -v sudo >/dev/null 2>&1; then
    sudo "$@"
  else
    printf 'This step requires root access, but sudo is not installed.\n' >&2
    exit 1
  fi
}

if [[ "$skip_dependencies" == false ]]; then
  printf 'Installing build dependencies for %s...\n' "${PRETTY_NAME:-$distro_id}"
  if [[ "$package_format" == "deb" ]]; then
    run_as_root apt-get update
    run_as_root apt-get install -y python3 python3-dev python3-pip python3-venv python3-tk build-essential dpkg-dev
  else
    run_as_root dnf install -y python3 python3-devel python3-pip python3-tkinter gcc make rpm-build
  fi
fi

for command_name in python3; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    printf 'Required command is unavailable: %s\n' "$command_name" >&2
    exit 1
  fi
done

if [[ "$package_format" == "deb" ]] && ! command -v dpkg-deb >/dev/null 2>&1; then
  printf 'dpkg-deb is unavailable. Re-run without --skip-dependencies.\n' >&2
  exit 1
fi
if [[ "$package_format" == "rpm" ]] && ! command -v rpmbuild >/dev/null 2>&1; then
  printf 'rpmbuild is unavailable. Re-run without --skip-dependencies.\n' >&2
  exit 1
fi

venv_dir="build/linux-venv"
python3 -m venv "$venv_dir"
"$venv_dir/bin/python" -m pip install --upgrade pip
"$venv_dir/bin/python" -m pip install -r requirements-build.txt
"$venv_dir/bin/python" -B -m unittest -v
"$venv_dir/bin/python" -m PyInstaller --noconfirm --clean --onefile --windowed \
  --name "$package_name" \
  --add-data "simple_rss.png:." \
  simple_rss.py

architecture="$(uname -m)"
case "$architecture" in
  x86_64) deb_arch="amd64"; rpm_arch="x86_64" ;;
  aarch64|arm64) deb_arch="arm64"; rpm_arch="aarch64" ;;
  *) printf 'Unsupported CPU architecture: %s\n' "$architecture" >&2; exit 1 ;;
esac

work_dir="build/linux-package"
rm -rf "$work_dir"
mkdir -p "$work_dir"

write_desktop_file() {
  destination="$1"
  mkdir -p "$(dirname "$destination")"
  printf '%s\n' \
    '[Desktop Entry]' \
    'Type=Application' \
    "Name=$app_name" \
    'Comment=Compact RSS and Atom feed reader' \
    "Exec=$package_name" \
    "Icon=$package_name" \
    'Terminal=false' \
    'Categories=Network;News;' > "$destination"
}

if [[ "$package_format" == "deb" ]]; then
  package_root="$work_dir/deb-root"
  mkdir -p "$package_root/DEBIAN" "$package_root/opt/$package_name" \
    "$package_root/usr/bin" "$package_root/usr/share/applications" \
    "$package_root/usr/share/icons/hicolor/256x256/apps"
  install -m 0755 "dist/$package_name" "$package_root/opt/$package_name/$package_name"
  ln -s "/opt/$package_name/$package_name" "$package_root/usr/bin/$package_name"
  install -m 0644 simple_rss.png "$package_root/usr/share/icons/hicolor/256x256/apps/$package_name.png"
  write_desktop_file "$package_root/usr/share/applications/$package_name.desktop"
  cat > "$package_root/DEBIAN/control" <<EOF
Package: $package_name
Version: $app_version
Section: net
Priority: optional
Architecture: $deb_arch
Maintainer: Eduardo A. de Carvalho
Description: Compact desktop RSS and Atom feed reader
 Simple RSS displays recent feed entries with selectable visual themes.
EOF
  artifact="dist/Simple_RSS_${app_version}_${deb_arch}.deb"
  dpkg-deb --root-owner-group --build "$package_root" "$artifact"
  if [[ "$install_package" == true ]]; then
    run_as_root apt-get install -y "./$artifact"
  fi
else
  rpm_root="$work_dir/rpmbuild"
  payload_root="$work_dir/rpm-payload"
  mkdir -p "$rpm_root/BUILD" "$rpm_root/BUILDROOT" "$rpm_root/RPMS" \
    "$rpm_root/SOURCES" "$rpm_root/SPECS" "$rpm_root/SRPMS" \
    "$payload_root/opt/$package_name" "$payload_root/usr/bin" \
    "$payload_root/usr/share/applications" "$payload_root/usr/share/icons/hicolor/256x256/apps"
  install -m 0755 "dist/$package_name" "$payload_root/opt/$package_name/$package_name"
  ln -s "/opt/$package_name/$package_name" "$payload_root/usr/bin/$package_name"
  install -m 0644 simple_rss.png "$payload_root/usr/share/icons/hicolor/256x256/apps/$package_name.png"
  write_desktop_file "$payload_root/usr/share/applications/$package_name.desktop"
  tar -C "$payload_root" -czf "$rpm_root/SOURCES/${package_name}-${app_version}.tar.gz" .
  cat > "$rpm_root/SPECS/$package_name.spec" <<EOF
Name:           $package_name
Version:        $app_version
Release:        1%{?dist}
Summary:        Compact desktop RSS and Atom feed reader
License:        Proprietary
BuildArch:      $rpm_arch
Source0:        %{name}-%{version}.tar.gz

%description
Simple RSS displays recent RSS and Atom entries with selectable visual themes.

%prep
%setup -q -c -T
tar -xzf %{SOURCE0}

%install
mkdir -p %{buildroot}
cp -a . %{buildroot}/

%files
/opt/$package_name/$package_name
/usr/bin/$package_name
/usr/share/applications/$package_name.desktop
/usr/share/icons/hicolor/256x256/apps/$package_name.png
EOF
  rpmbuild --define "_topdir $(pwd)/$rpm_root" -bb "$rpm_root/SPECS/$package_name.spec"
  built_rpm="$(find "$rpm_root/RPMS" -type f -name '*.rpm' -print -quit)"
  artifact="dist/Simple_RSS_${app_version}_${rpm_arch}.rpm"
  cp "$built_rpm" "$artifact"
  if [[ "$install_package" == true ]]; then
    run_as_root dnf install -y "$artifact"
  fi
fi

printf '\nBuilt %s\n' "$artifact"
if command -v sha256sum >/dev/null 2>&1; then
  sha256sum "$artifact"
else
  shasum -a 256 "$artifact"
fi
