import subprocess
from datetime import datetime
import os
from pathlib import Path
import stat # Import stat module for checking mount points

# Assuming scripts are in a 'scripts' directory relative to runner.py or an absolute path
# This will be passed from main.py
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"

LOGFILE = os.path.expanduser("~/.cache/helwan-rescue/history.log")
try:
    os.makedirs(os.path.dirname(LOGFILE), exist_ok=True)
except Exception:
    # Fallback if user's home directory isn't writable (e.g., Live USB without home set up)
    LOGFILE = "/tmp/helwan-rescue.log"

# Global variable to track chroot status
# This will be updated by the GUI after running open_chroot.sh
IS_CHROOT_ACTIVE = False

def log_operation(script_name: str, output: str, success: bool = True):
    """Logs the operation to a history file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "OK" if success else "FAIL"
    try:
        with open(LOGFILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {script_name} - {status}\n")
            f.write(output.strip() + "\n\n")
    except Exception as e:
        # If logging fails, print to stderr (e.g., if /tmp also becomes unwritable)
        print(f"Error writing to log file {LOGFILE}: {e}", file=sys.stderr)


def check_chroot_status() -> bool:
    """
    Checks if /mnt is mounted, indicating a potential chroot environment is ready.
    This is a basic check. A more robust check might involve /proc/mounts.
    """
    # Check if /mnt exists and is a mount point
    if os.path.ismount("/mnt"):
        return True
    return False

def run_script(script_name: str, args: list = None, chroot_aware: bool = True, interactive_input: str = None) -> (bool, str):
    """
    Runs a shell script, optionally within a chroot environment, and captures output.

    Args:
        script_name: The name of the script file (e.g., "fix_grub.sh").
        args: A list of arguments to pass to the script.
        chroot_aware: If True, the script will be run with 'arch-chroot /mnt' if IS_CHROOT_ACTIVE is True.
        interactive_input: String to pass as stdin to the script for interactive prompts.

    Returns:
        A tuple: (success: bool, output: str)
    """
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        output = f"Error: Script not found: {script_path}"
        log_operation(script_name, output, success=False)
        return False, output

    command_prefix = []
    global IS_CHROOT_ACTIVE
    # Update chroot status right before running a chroot-aware script
    IS_CHROOT_ACTIVE = check_chroot_status()

    if chroot_aware and IS_CHROOT_ACTIVE:
        command_prefix = ["arch-chroot", "/mnt"]
        print(f"Running script '{script_name}' within chroot.")
    else:
        print(f"Running script '{script_name}' directly.")

    full_command = command_prefix + ["bash", str(script_path)] + (args if args else [])

    print(f"Executing command: {' '.join(full_command)}") # For debugging

    try:
        process = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            input=interactive_input, # Pass input to stdin
            check=False # Do not raise CalledProcessError on non-zero exit codes
        )
        output = process.stdout + process.stderr
        success = (process.returncode == 0)

        log_operation(script_name, output, success)
        return success, output
    except FileNotFoundError:
        output = f"Error: 'bash' or 'arch-chroot' command not found. Ensure required tools are installed."
        log_operation(script_name, output, success=False)
        return False, output
    except Exception as e:
        output = f"An unexpected error occurred: {e}"
        log_operation(script_name, output, success=False)
        return False, output
