#!/usr/bin/env bash

set -euo pipefail

readonly COMPOSE_PROJECT_NAME="flowdesk-test"
readonly COMPOSE_FILE="compose.test.yaml"
readonly ENV_FILE="${FLOWDESK_TEST_ENV_FILE:-.env.test}"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing ${ENV_FILE}. Copy .env.test.example and provide test-only values." >&2
  exit 1
fi

compose() {
  docker compose \
    --project-name "${COMPOSE_PROJECT_NAME}" \
    --env-file "${ENV_FILE}" \
    --file "${COMPOSE_FILE}" \
    "$@"
}

cleanup() {
  compose down --volumes --remove-orphans >/dev/null 2>&1 || true
}

cleanup
trap cleanup EXIT

compose config --quiet
compose build migrate tests
compose up --wait postgres rabbitmq
compose run --rm --no-deps migrate
compose run --rm --no-deps tests \
  uv run pytest \
  --cov=src \
  --cov-branch \
  --cov-report=term-missing \
  --cov-report=html
