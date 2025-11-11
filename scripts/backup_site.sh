#!/usr/bin/env bash
set -Eeuo pipefail

# Frappe/Bench site backup helper
# - Creates a logical backup using `bench --site <site> backup`
# - Optional: include public/private files with --with-files
# - Retains backups for N days (default 2), effectively keeping current + previous 2 days
# - Logs to <BENCH_DIR>/logs/backup.log

# Defaults (can be overridden via flags or env)
SITE="${SITE:-crm.localhost}"
RETENTION_DAYS="${RETENTION_DAYS:-2}"  # delete files older than this many days
WITH_FILES="${WITH_FILES:-false}"

# Resolve bench dir: default to repo root when script is placed at apps/crm/scripts
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_BENCH_DIR="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
BENCH_DIR="${BENCH_DIR:-${DEFAULT_BENCH_DIR}}"

BACKUP_DIR="${BENCH_DIR}/sites/${SITE}/private/backups"
LOG_DIR="${BENCH_DIR}/logs"
LOG_FILE="${LOG_DIR}/backup.log"

usage() {
  cat <<EOF
Usage: $(basename "$0") [--site SITE] [--bench-dir PATH] [--retention-days N] [--with-files true|false]

Options:
  --site             Frappe site name (default: ${SITE})
  --bench-dir        Bench directory (default: ${BENCH_DIR})
  --retention-days   Delete backups older than N days (default: ${RETENTION_DAYS})
  --with-files       Include public/private files (default: ${WITH_FILES})
  -h, --help         Show this help

Environment variables (alternative to flags): SITE, BENCH_DIR, RETENTION_DAYS, WITH_FILES
EOF
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --site)
        SITE="$2"; shift 2 ;;
      --bench-dir)
        BENCH_DIR="$2"; shift 2 ;;
      --retention-days)
        RETENTION_DAYS="$2"; shift 2 ;;
      --with-files)
        WITH_FILES="$2"; shift 2 ;;
      -h|--help)
        usage; exit 0 ;;
      *)
        echo "Unknown argument: $1" >&2; usage; exit 1 ;;
    esac
  done
}

timestamp() { date +"%Y-%m-%d %H:%M:%S"; }

run_backup() {
  cd "${BENCH_DIR}"
  # Prefer bench inside bench env if available
  export PATH="${BENCH_DIR}/env/bin:${PATH}"

  if [[ "${WITH_FILES}" == "true" ]]; then
    bench --site "${SITE}" backup --with-files
  else
    bench --site "${SITE}" backup
  fi
}

ensure_dirs() {
  mkdir -p "${BACKUP_DIR}" "${LOG_DIR}"
}

delete_old_backups() {
  # Delete files older than RETENTION_DAYS
  # Typical names:
  #   *-database.sql.gz
  #   *-public-files.tar
  #   *-private-files.tar
  # Also match tar.gz/tgz just in case
  find "${BACKUP_DIR}" -type f \
    \( -name "*.sql.gz" -o -name "*.tar" -o -name "*.tar.gz" -o -name "*.tgz" \) \
    -mtime +"${RETENTION_DAYS}" -print -delete || true
}

report_latest_paths() {
  # Echo latest created backup files to STDOUT for external consumers
  local latest_db latest_priv latest_pub
  latest_db=$(ls -1t "${BACKUP_DIR}"/*-database.sql.gz 2>/dev/null | head -n 1 || true)
  latest_priv=$(ls -1t "${BACKUP_DIR}"/*-private-files.tar 2>/dev/null | head -n 1 || true)
  latest_pub=$(ls -1t "${BACKUP_DIR}"/*-public-files.tar 2>/dev/null | head -n 1 || true)

  [[ -n "${latest_db:-}" ]] && echo "DB_BACKUP=${latest_db}"
  [[ -n "${latest_priv:-}" ]] && echo "PRIVATE_FILES_BACKUP=${latest_priv}"
  [[ -n "${latest_pub:-}" ]] && echo "PUBLIC_FILES_BACKUP=${latest_pub}"
}

main() {
  parse_args "$@"
  ensure_dirs

  {
    echo "[$(timestamp)] Starting backup | site=${SITE} bench_dir=${BENCH_DIR} with_files=${WITH_FILES} retention_days=${RETENTION_DAYS}"
    echo "[$(timestamp)] Backup directory: ${BACKUP_DIR}"

    local count_before count_after
    count_before=$(ls -1 "${BACKUP_DIR}" 2>/dev/null | wc -l || true)

    run_backup

    count_after=$(ls -1 "${BACKUP_DIR}" 2>/dev/null | wc -l || true)
    echo "[$(timestamp)] Backup completed | files_before=${count_before} files_after=${count_after}"

    echo "[$(timestamp)] Applying retention policy (delete older than ${RETENTION_DAYS} days)"
    delete_old_backups | sed 's/^/[deleted] /' || true

    echo "[$(timestamp)] Recent backups:"
    ls -1t "${BACKUP_DIR}" 2>/dev/null | head -n 10 | sed 's/^/  /' || true
    echo "[$(timestamp)] Done"
  } >> "${LOG_FILE}" 2>&1

  # Print latest paths to STDOUT for callers (e.g., client-side fetchers)
  report_latest_paths
}

main "$@"


