#!/bin/bash

if [ "$RUN_HUEY" ]; then
    __RUN_HUEY=1
fi

if [ -f /.env ]; then
    source /.env
fi

if [ "$#" = 0 ]; then
    if [ "${__RUN_HUEY}" ]; then
        if [ -z "$HUEY_WORKERS" ]; then
            HUEY_WORKERS="$(python -c 'import multiprocessing as m; print(max(m.cpu_count() * 3, 6))')"
        fi
        CMD="./manage.py run_huey --workers $HUEY_WORKERS --flush-locks"
        if [ "$DEBUG" -a "$DEBUG" != '0' ]; then
            exec watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- $CMD
        else
            exec $CMD
        fi
    else
        echo "Starting up Crazy Arms Radio Backend version $CRAZYARMS_VERSION"

        wait-for-it -t 0 db:5432

        # TODO: detect version change and clear redis

        ./manage.py migrate
        ./manage.py init_services

        if [ "$DEBUG" -a "$DEBUG" != '0' ]; then
            exec ./manage.py runserver
        else
            ./manage.py collectstatic --noinput

            if [ -z "$GUNICORN_WORKERS" ]; then
                GUNICORN_WORKERS="$(python -c 'import multiprocessing as m; print(max(round(m.cpu_count() * 1.5 + 1), 3))')"
            fi

            exec gunicorn $GUNICORN_ARGS --forwarded-allow-ips '*' -b 0.0.0.0:8000 -w $GUNICORN_WORKERS --capture-output --access-logfile - crazyarms.wsgi
        fi
    fi
else
    exec "$@"
fi
