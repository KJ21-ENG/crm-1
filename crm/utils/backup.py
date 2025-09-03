import os
import subprocess
import frappe


def run_system_backup_script():
    """Wrapper called by scheduler cron to run the backup_eshin_site.sh script.

    This uses subprocess to invoke the script with the repository's bench
    directory as the working directory. Any output or error is logged via
    Frappe's logger so admins can inspect failures in the error log.
    """

    try:
        bench_dir = os.path.abspath(frappe.get_site_path("..", ".."))
    except Exception:
        # Fallback to repo root relative location
        bench_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

    script_path = os.path.abspath(os.path.join(bench_dir, "apps", "crm", "scripts", "backup_eshin_site.sh"))

    if not os.path.isfile(script_path):
        frappe.log_error(f"Backup script not found at {script_path}", "crm.utils.backup.run_system_backup_script")
        return

    try:
        # Ensure executable
        os.chmod(script_path, 0o755)
        # Run script; do not block frappe scheduler for too long — this will run
        # synchronously but output is captured and logged.
        proc = subprocess.run([script_path], cwd=bench_dir, capture_output=True, text=True, timeout=60 * 60)
        if proc.returncode != 0:
            frappe.log_error(f"Backup script failed: {proc.returncode}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}", "crm.utils.backup.run_system_backup_script")
        else:
            frappe.logger().debug(f"Backup script completed successfully. stdout:\n{proc.stdout}")
    except Exception as e:
        frappe.log_error(f"Error running backup script: {str(e)}", "crm.utils.backup.run_system_backup_script")


def run_bench_backup_script():
    """Wrapper to run `apps/crm/scripts/backup_site.sh` (the more generic backup helper).

    This mirrors `run_system_backup_script` but points to `backup_site.sh` and is
    intended to be scheduled separately (e.g., at 17:00 daily).
    """

    try:
        bench_dir = os.path.abspath(frappe.get_site_path("..", ".."))
    except Exception:
        # Fallback to repo root relative location
        bench_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

    script_path = os.path.abspath(os.path.join(bench_dir, "apps", "crm", "scripts", "backup_site.sh"))

    if not os.path.isfile(script_path):
        frappe.log_error(f"Backup script not found at {script_path}", "crm.utils.backup.run_bench_backup_script")
        return

    try:
        os.chmod(script_path, 0o755)
        proc = subprocess.run([script_path], cwd=bench_dir, capture_output=True, text=True, timeout=60 * 60)
        if proc.returncode != 0:
            frappe.log_error(f"backup_site.sh failed: {proc.returncode}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}", "crm.utils.backup.run_bench_backup_script")
        else:
            frappe.logger().debug(f"backup_site.sh completed successfully. stdout:\n{proc.stdout}")
    except Exception as e:
        frappe.log_error(f"Error running backup_site.sh: {str(e)}", "crm.utils.backup.run_bench_backup_script")


