#!/usr/bin/env bash
set -e

docker compose exec backend python manage.py test
