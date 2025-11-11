#!/usr/bin/env bash
set -Eeuo pipefail

# backup_eshin_site.sh
# Created for EC2 host usage. Defaults are set for the provided server details.
# - SITE default: eshin.in
# - BENCH_DIR default: /home/ubuntu/frappe-bench
# - Retention: keep current + previous 2 days (delete files older than 2 days)
# - Includes public/private files by default

SITE="${SITE:-eshin.in}"
BENCH_DIR="${BENCH_DIR:-/home/ubuntu/frappe-bench}"
RETENTION_DAYS="${RETENTION_DAYS:-2}"
WITH_FILES="${WITH_FILES:-true}"

BACKUP_DIR="${BENCH_DIR}/sites/${SITE}/private/backups"
LOG_DIR="${BENCH_DIR}/logs"
LOG_FILE="${LOG_DIR}/backup_eshin.log"

timestamp() { date +"%Y-%m-%d %H:%M:%S"; }

usage() {
  cat <<EOF
Usage: $(basename "$0") [--site SITE] [--bench-dir PATH] [--retention-days N] [--with-files true|false]

Defaults: SITE=${SITE} BENCH_DIR=${BENCH_DIR} RETENTION_DAYS=${RETENTION_DAYS} WITH_FILES=${WITH_FILES}
EOF
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --site) SITE="$2"; shift 2 ;;
      --bench-dir) BENCH_DIR="$2"; shift 2 ;;
      --retention-days) RETENTION_DAYS="$2"; shift 2 ;;
      --with-files) WITH_FILES="$2"; shift 2 ;;
      -h|--help) usage; exit 0 ;;
      *) echo "Unknown arg: $1" >&2; usage; exit 1 ;;
    esac
  done
}

ensure_dirs() {
  mkdir -p "${BACKUP_DIR}" "${LOG_DIR}"
}

run_backup() {
  cd "${BENCH_DIR}"
  export PATH="${BENCH_DIR}/env/bin:${PATH}"

  if [[ "${WITH_FILES}" == "true" ]]; then
    bench --site "${SITE}" backup --with-files
  else
    bench --site "${SITE}" backup
  fi
}

delete_old_backups() {
  find "${BACKUP_DIR}" -type f \
    \( -name "*.sql.gz" -o -name "*.tar" -o -name "*.tar.gz" -o -name "*.tgz" -o -name "*site_config_backup.json" \) \
    -mtime +"${RETENTION_DAYS}" -print -delete || true
}

report_latest() {
  local latest_db latest_priv latest_pub
  latest_db=$(ls -1t "${BACKUP_DIR}"/*-database.sql.gz 2>/dev/null | head -n 1 || true)
  latest_priv=$(ls -1t "${BACKUP_DIR}"/*-private-files.tar 2>/dev/null | head -n 1 || true)
  latest_pub=$(ls -1t "${BACKUP_DIR}"/*-public-files.tar 2>/dev/null | head -n 1 || true)

  [[ -n "${latest_db}" ]] && echo "DB_BACKUP=${latest_db}"
  [[ -n "${latest_priv}" ]] && echo "PRIVATE_FILES_BACKUP=${latest_priv}"
  [[ -n "${latest_pub}" ]] && echo "PUBLIC_FILES_BACKUP=${latest_pub}"
}

main() {
  parse_args "$@"
  ensure_dirs

  {
    echo "[$(timestamp)] Starting eshin.in backup | site=${SITE} bench_dir=${BENCH_DIR} with_files=${WITH_FILES} retention_days=${RETENTION_DAYS}"
    echo "[$(timestamp)] Backup directory: ${BACKUP_DIR}"

    local before after
    before=$(ls -1 "${BACKUP_DIR}" 2>/dev/null | wc -l || true)

    run_backup

    after=$(ls -1 "${BACKUP_DIR}" 2>/dev/null | wc -l || true)
    echo "[$(timestamp)] Backup completed | files_before=${before} files_after=${after}"

    echo "[$(timestamp)] Applying retention (delete files older than ${RETENTION_DAYS} days)"
    delete_old_backups | sed 's/^/[deleted] /' || true

    echo "[$(timestamp)] Recent backups:" 
    ls -1t "${BACKUP_DIR}" 2>/dev/null | head -n 10 | sed 's/^/  /' || true
    echo "[$(timestamp)] Done"
  } >> "${LOG_FILE}" 2>&1

  report_latest
}

main "$@"


