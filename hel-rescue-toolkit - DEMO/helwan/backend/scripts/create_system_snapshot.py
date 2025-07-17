import os
import platform
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

def is_root():
    if platform.system() == "Windows":
        # على ويندوز، غالبًا بتكون مشغل كأدمن أو تتجاهل الفحص
        return True
    else:
        return os.geteuid() == 0

def get_home_directory():
    return Path.home()

def create_snapshot():
    if not is_root():
        print("⚠️ Please run this tool as administrator/root!")
        return

    # اسم مجلد السحب بالوقت
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    snapshot_dir = get_home_directory() / f"helwan_snapshot_{timestamp}"
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    print(f"[+] Creating snapshot at: {snapshot_dir}")

    # مجلدات مستهدفة - عدل حسب النظام
    folders_to_copy = []

    if platform.system() == "Windows":
        folders_to_copy = [
            os.path.join(os.environ["SystemRoot"], "System32"),
            os.path.join(os.environ["USERPROFILE"], "Documents"),
        ]
    else:  # Linux or macOS
        folders_to_copy = [
            "/etc",
            "/var/log",
            str(get_home_directory())
        ]

    # نسخ المجلدات
    for folder in folders_to_copy:
        folder_path = Path(folder)
        if folder_path.exists():
            dest = snapshot_dir / folder_path.name
            try:
                print(f"[+] Copying {folder} → {dest}")
                shutil.copytree(folder_path, dest, dirs_exist_ok=True)
            except Exception as e:
                print(f"[!] Failed to copy {folder}: {e}")

    # ضغط المجلد
    zip_path = f"{snapshot_dir}.zip"
    print(f"[+] Compressing snapshot to {zip_path}")
    shutil.make_archive(str(snapshot_dir), 'zip', str(snapshot_dir))

    # حذف النسخة غير المضغوطة
    print(f"[+] Cleaning up folder {snapshot_dir}")
    shutil.rmtree(snapshot_dir)

    print("[✓] Snapshot created successfully.")

# للتشغيل كأداة مستقلة
if __name__ == "__main__":
    create_snapshot()
