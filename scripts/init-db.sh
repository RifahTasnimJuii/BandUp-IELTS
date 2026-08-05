#!/usr/bin/env bash
set -e

export PGPASSWORD=${DATABASE_PASSWORD:-bandup_pass}
psql -h ${DATABASE_HOST:-localhost} -U ${DATABASE_USER:-bandup} -d ${DATABASE_NAME:-bandup_ielts} -c "SELECT 1;"
