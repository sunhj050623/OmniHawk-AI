#!/bin/bash
set -e

# Validate required config files.
if [ ! -f "/app/config/config.yaml" ] || [ ! -f "/app/config/frequency_words.txt" ]; then
    echo "ERROR: missing required config files (/app/config/config.yaml or /app/config/frequency_words.txt)"
    exit 1
fi

case "${RUN_MODE:-cron}" in
"once")
    echo "RUN_MODE=once: starting one-shot crawl"
    exec omnihawk-ai
    ;;
"panel")
    PANEL_PORT="${WEBSERVER_PORT:-8080}"
    PANEL_OUTPUT_DIR="${PANEL_OUTPUT_DIR:-/app/output}"
    echo "RUN_MODE=panel: starting OmniHawk AI panel server on port ${PANEL_PORT}"
    exec python -m omnihawk_ai.web.panel_server --port "${PANEL_PORT}" --output-dir "${PANEL_OUTPUT_DIR}"
    ;;
"cron")
    # Validate cron expression with a conservative character whitelist.
    CRON_EXPR="${CRON_SCHEDULE:-*/30 * * * *}"
    if ! echo "$CRON_EXPR" | grep -qE '^[0-9*/,[:space:]-]+$'; then
        echo "ERROR: invalid CRON_SCHEDULE: $CRON_EXPR"
        exit 1
    fi

    # Build supercronic crontab.
    echo "$CRON_EXPR cd /app && omnihawk-ai" > /tmp/crontab
    echo "Generated crontab:"
    cat /tmp/crontab

    if ! /usr/local/bin/supercronic -test /tmp/crontab; then
        echo "ERROR: crontab validation failed"
        exit 1
    fi

    # Optional immediate run before scheduler starts.
    if [ "${IMMEDIATE_RUN:-false}" = "true" ]; then
        echo "Running immediate crawl before scheduler starts"
        omnihawk-ai
    fi

    echo "Starting static web server"
    python manage.py start_webserver

    echo "Starting supercronic: $CRON_EXPR"
    exec /usr/local/bin/supercronic -passthrough-logs -inotify /tmp/crontab
    ;;
*)
    exec "$@"
    ;;
esac
