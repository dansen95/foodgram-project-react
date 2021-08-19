FROM python:3.8.5

WORKDIR /code
COPY . .
RUN pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
RUN python manage.py collectstatic --noinput
CMD gunicorn backend.wsgi:application --bind 0.0.0.0:8000