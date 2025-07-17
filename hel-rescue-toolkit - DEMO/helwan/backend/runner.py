import subprocess
import os
from pathlib import Path
import datetime

# Define the base directory for scripts.
# This will be updated by main.py to ensure consistency.
SCRIPTS_DIR = Path("/usr/share/helwan/scripts") # Default or placeholder path

# Log file for all operations
LOGFILE = Path("/var/log/helwan-rescue-toolkit.log")

def _log_message(message):
    """Appends a message with a timestamp to the log file."""
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    try:
        # Ensure the log directory exists if not in /tmp
        if not LOGFILE.parent.exists():
            LOGFILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOGFILE, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} {message}\n")
    except IOError as e:
        # Fallback to printing if logging to file fails
        print(f"Error writing to log file {LOGFILE}: {e}")
        print(f"{timestamp} {message}")

def run_script_async(script_path, *args):
    """
    Runs a script (shell or python) asynchronously and logs its start.
    Returns the command list for QProcess.
    """
    if script_path.suffix == '.py':
        full_command = ["python", str(script_path)] + list(args) # تم التغيير من "python3" إلى "python"
    else: # Default to bash for .sh scripts or others
        full_command = ["bash", str(script_path)] + list(args)
            
    _log_message(f"Executing: {' '.join(full_command)}")
    return full_command


def check_chroot_status():
    """
    Checks if the system is currently running inside a chroot environment.
    Returns True if inside chroot, False otherwise.
    """
    try:
        # Compare device numbers of / and /proc/1/root/
        # If they are different, it means we are in a chroot.
        # This is a common and reliable method.
        stat_root = os.stat("/")
        stat_proc_root = os.stat("/proc/1/root/")
        return stat_root.st_dev != stat_proc_root.st_dev
    except Exception:
        # In case /proc/1/root/ is not accessible or other errors
        return False
