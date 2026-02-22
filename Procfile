release: python manage.py migrate --settings=majobacore.settings.production --noinput
web: gunicorn majobacore.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --access-logfile - --error-logfile -
