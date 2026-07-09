pkgname=markdown-editor
pkgver=0.2.1
pkgrel=1
pkgdesc="A Markdown editor with live preview"
arch=('any')
url="https://github.com/oyebayo/markdown-editor"
license=("MIT")
depends=("python" "gtk4" "libadwaita" "gtksourceview5" "python-mistune" "python-pygments" "python-latex2mathml")
makedepends=("python" "python-build" "python-installer" "python-setuptools" "python-wheel" "git")

source=("git+https://github.com/oyebayo/markdown-editor.git")
sha256sums=("SKIP")

pkgver() {
    cd "$srcdir/$pkgname"
    local _tag
    _tag=$(git describe --tags --abbrev=0)
    printf "%s" "${_tag#v}"
}

build() {
  cd "$srcdir/$pkgname"
  python -m build --wheel --no-isolation 2>&1 | tail -10
}

package() {
  cd "$srcdir/$pkgname"
  python -m installer --destdir="$pkgdir" dist/*.whl

  # Install icon
  install -Dm644 assets/$pkgname.svg "$pkgdir/usr/share/icons/hicolor/scalable/apps/$pkgname.svg"

  # Install desktop file
  install -Dm644 assets/$pkgname.desktop "$pkgdir/usr/share/applications/$pkgname.desktop"
  sed -i "s|^Exec=.*|Exec=/usr/bin/$pkgname %F|" "$pkgdir/usr/share/applications/$pkgname.desktop"
}
