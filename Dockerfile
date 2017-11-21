FROM quay.io/pik-software/base:v1.6

ENV PYTHONUNBUFFERED 1

RUN mkdir -p /app /static /media /cache && chown -R unprivileged:unprivileged /media /cache
WORKDIR /app

COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

COPY ./docker-entrypoint.sh /docker-entrypoint.sh

ENV STATIC_ROOT /static
ENV MEDIA_ROOT /media

COPY . /app
RUN /app/docker-prepare.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
