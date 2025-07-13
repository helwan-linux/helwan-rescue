# Maintainer: Saeed Badrelden <you@example.com>
pkgname=helwan-rescue-toolkit
pkgver=1.0.0
pkgrel=1
pkgdesc="Essential recovery GUI tools for Helwan Linux"
arch=('any')
url="https://github.com/helwan-linux/helwan-rescue"
license=('GPL')
depends=('python' 'python-pyqt5')
source=("hel-rescue-toolkit::git+https://github.com/helwan-linux/helwan-rescue.git")
md5sums=('SKIP')

package() {
  # نسخ الملفات الرئيسية
  install -d "$pkgdir/opt/$pkgname"
  cp -r "$srcdir/hel-rescue-toolkit/"* "$pkgdir/opt/$pkgname/"

  # صلاحيات السكربتات
  find "$pkgdir/opt/$pkgname/backend/scripts/" -type f -name "*.sh" -exec chmod +x {} \;
  chmod +x "$pkgdir/opt/$pkgname/run.sh"

  # إنشاء ملف .desktop
  install -Dm644 "$pkgdir/opt/$pkgname/helwan-rescue.desktop" "$pkgdir/usr/share/applications/helwan-rescue.desktop"

  # نسخ الأيقونة إلى المسار الصحيح
  install -Dm644 "$pkgdir/opt/$pkgname/helwan/resources/icons/logo.png" \
    "$pkgdir/usr/share/icons/hicolor/256x256/apps/helwan-rescue.png"
}
