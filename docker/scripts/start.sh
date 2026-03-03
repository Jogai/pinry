#!/bin/bash
# -----------------------------------------------------------------------------
# docker-pinry /start script
#
# Will setup database and static files if they don't exist already, if they do
# just continues to run docker-pinry.
#
# Authors: Isaac Bythewood
# Updated: Aug 19th, 2014
# -----------------------------------------------------------------------------
PROJECT_ROOT="/pinry"

bash ${PROJECT_ROOT}/docker/scripts/bootstrap.sh

# If static files don't exist collect them
cd ${PROJECT_ROOT}
python manage.py collectstatic --noinput

# If database doesn't exist yet create it
if [ ! -f /data/production.db ]
then
    cd ${PROJECT_ROOT}
    python manage.py migrate --noinput
fi

# Fix all settings after all commands are run
chown -R www-data:www-data /data

# Auto-tag cron (daily at 3 AM UTC; set AUTO_TAG_CRON_ENABLED=false to disable)
if [ "${AUTO_TAG_CRON_ENABLED:-true}" = "true" ]; then
    SCHEDULE="${AUTO_TAG_CRON_SCHEDULE:-0 3 * * *}"
    LIMIT="${AUTO_TAG_CRON_LIMIT:-500}"
    printf '%s www-data cd /pinry && python manage.py auto_tag_pins --limit %s >> /data/auto_tag.log 2>&1\n' \
        "${SCHEDULE}" "${LIMIT}" > /etc/cron.d/pinry-auto-tag
    chmod 0644 /etc/cron.d/pinry-auto-tag
    service cron start 2>/dev/null || true
fi

# start all process
/usr/sbin/nginx

cd ${PROJECT_ROOT}
./docker/scripts/_start_gunicorn.sh
