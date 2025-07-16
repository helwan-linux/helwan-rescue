# Maintainer: Your Name <your_email@example.com>
pkgname=helwan-rescue-toolkit
pkgver=1.0.0 # You can update this version number as you develop
pkgrel=1
pkgdesc="A comprehensive GUI-based rescue toolkit for Arch Linux systems."
arch=('any') # 'any' because it's a Python script, not architecture-specific
url="https://github.com/yourusername/helwan-rescue-toolkit" # Optional: Replace with your project's URL
license=('MIT') # Or whatever license you choose
depends=('python' 'python-pyqt5' 'arch-install-scripts' 'btrfs-progs' 'tar' 'util-linux' 'coreutils' 'grep' 'awk' 'sed' 'findutils' 'iproute2' 'networkmanager' 'grub' 'mkinitcpio' 'procps') # Add all necessary dependencies
makedepends=('python-setuptools') # For Python packaging

# The source array defines what files makepkg needs to download or locate.
# For a local project, we'll use a local source.
# The '::' prefix tells makepkg to use the local directory as source.
source=("${pkgname}-${pkgver}.tar.gz::./"
        "${pkgname}.desktop"
        )
# A simple wrapper script to run the Python application with sudo
# This will be installed to /usr/bin
install="${pkgname}.install" # Optional: for post-install messages/actions, not needed for now


prepare() {
    # This function is used to prepare the source code if necessary
    # For a simple Python project, we might just need to ensure permissions or prepare for setuptools
    # Or, we can just pack the entire project directory into a tarball as source
    # For simplicity, we'll assume the project root is what we're packaging.
    # No specific prepare step needed if we package the whole directory and install directly.
    echo "Preparing source..."
}

build() {
    # This function is for building the package (e.g., compiling C code, running setup.py build)
    # For a pure Python script, this is often empty or just runs setuptools build
    # We will just copy files directly in package(), so this can be empty.
    echo "No specific build steps needed for this Python application."
}

package() {
    # This function installs files into the fakeroot environment (pkg/)
    # These files will then be packed into the .zst archive.

    # 1. Create necessary directories in the fakeroot
    install -d "${pkgdir}/usr/bin"
    install -d "${pkgdir}/usr/lib/${pkgname}"
    install -d "${pkgdir}/usr/share/applications"
    install -d "${pkgdir}/usr/share/icons/hicolor/scalable/apps" # For scalable SVG/PNG
    install -d "${pkgdir}/usr/share/doc/${pkgname}"

    # 2. Copy Python application files
    # Copy the entire 'helwan' directory (which contains main.py, backend/, resources/)
    cp -r "${srcdir}/helwan" "${pkgdir}/usr/lib/${pkgname}/"

    # 3. Create the executable wrapper script in /usr/bin
    cat <<EOF >"${pkgdir}/usr/bin/${pkgname}-toolkit"
#!/bin/bash
sudo python3 /usr/lib/${pkgname}/helwan/run.py "\$@"
EOF
    chmod +x "${pkgdir}/usr/bin/${pkgname}-toolkit" # Make it executable

    # 4. Install the .desktop file
    install -m644 "${srcdir}/helwan/resources/helwan-rescue.desktop" "${pkgdir}/usr/share/applications/${pkgname}.desktop"

    # 5. Install the main application icon
    # Assuming logo.png is the main icon and you want it as 'helwan-rescue-toolkit.png'
    install -m644 "${srcdir}/helwan/resources/icons/logo.png" "${pkgdir}/usr/share/icons/hicolor/scalable/apps/${pkgname}-toolkit.png"

    # 6. Install other icons if desired (e.g., for toolbar) - if they are used by the app itself
    # If your app dynamically loads these, you might need to install them to a different path
    # or ensure they are bundled with the python files. For simplicity, we only install the main desktop icon.
    # If you want other icons (about.png, help.png) to be available globally (e.g., for system themes),
    # you'd install them similarly, but the python code needs to reference them via icon themes or absolute paths.
    # For this project, they are bundled within the `helwan/resources/icons` and referenced by `main.py` directly.

    # 7. Install documentation (usage_help.txt)
    install -m644 "${srcdir}/helwan/resources/usage_help.txt" "${pkgdir}/usr/share/doc/${pkgname}/"
}