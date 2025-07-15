import subprocess
from datetime import datetime
import os
# from PyQt5.QtWidgets import QMessageBox # لم نعد نحتاجها هنا

LOGFILE = os.path.expanduser("~/.cache/helwan-rescue/history.log")
try:
    os.makedirs(os.path.dirname(LOGFILE), exist_ok=True)
except Exception:
    LOGFILE = "/tmp/helwan-rescue.log"

def log_operation(script_name, output, success=True):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "OK" if success else "FAIL"
    try:
        with open(LOGFILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {script_name} - {status}\n")
            f.write(output.strip() + "\n\n")
    except Exception:
        pass

def run_script(script_path):
    if not script_path.exists():
        # QMessageBox.critical(None, "Error", f"Script not found:\n{script_path}") # تم إزالة هذا
        return False, f"Error: Script not found:\n{script_path}" # إرجاع الخطأ

    result = subprocess.run(["bash", str(script_path)], capture_output=True, text=True)
    if result.returncode == 0:
        log_operation(script_path.name, result.stdout)
        # QMessageBox.information(None, "Success", result.stdout or "Done ✅") # تم إزالة هذا
        return True, result.stdout or "Done ✅" # إرجاع النجاح والمخرجات
    else:
        log_operation(script_path.name, result.stderr, success=False)
        # QMessageBox.warning(None, "Failed", result.stderr or "Unknown error.") # تم إزالة هذا
        return False, result.stderr or "Unknown error." # إرجاع الفشل والمخرجات
