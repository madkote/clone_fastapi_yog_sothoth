# Build stage
FROM python:3.7-alpine AS builder

ARG PYTHONUNBUFFERED=1
ARG REQ_PIPENV_VERSION=2018.11.26
ARG REQ_PIPENV_HASH=sha256:56ad5f5cb48f1e58878e14525a6e3129d4306049cb76d2f6a3e95df0d5fc6330
ARG REQ_CERTIFI_VERSION=2019.6.16
ARG REQ_CERTIFI_HASH=sha256:046832c04d4e752f37383b628bc601a7ea7211496b4638f6514d0e5b9acc4939
ARG REQ_VIRTUALENV_VERSION=16.6.1
ARG REQ_VIRTUALENV_HASH=sha256:d28ca64c0f3f125f59cabf13e0a150e1c68e5eea60983cc4395d88c584495783
ARG REQ_VIRTUALENV_CLONE_VERSION=0.5.3
ARG REQ_VIRTUALENV_CLONE_HASH=sha256:532f789a5c88adf339506e3ca03326f20ee82fd08ee5586b44dc859b5b4468c5

RUN apk update \
    && apk add --no-cache \
        build-base \
        libffi-dev \
        openssl-dev \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/cache/apk/*

# Export Yog Sothoth API requirements file
COPY . /src/
RUN cd /src/ \
    # install poetry
    && pip install --no-cache-dir --requirement poetry.requirements.txt \
    # export app requirements
    && poetry export --format requirements.txt --output app.requirements.txt \
    # build app
    && poetry build --format wheel

# Install app
FROM python:3.7-alpine as installer

# Define app version
ARG APP_VERSION=0.1.0

ARG PYTHONUNBUFFERED=1

RUN apk update \
    && apk add --no-cache \
        build-base \
        libffi-dev \
   && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/cache/apk/*

# Bring files from the build stage
COPY --from=builder /src/app.requirements.txt /tmp/app/
COPY --from=builder "/src/dist/yog_sothoth-${APP_VERSION}-py3-none-any.whl" /tmp/app/

# Install app
RUN pip install --no-cache-dir --requirement /tmp/app/app.requirements.txt \
    && pip install --no-cache-dir "/tmp/app/yog_sothoth-${APP_VERSION}-py3-none-any.whl"

# Final stage
FROM python:3.7-alpine

LABEL description="Docker image for Yog Sothoth API"
LABEL maintainer="HacKan <hackan@rlab.be>"
LABEL vendor="R'lyeh Hacklab Sysadmins"
LABEL vendor.url="https://adm.rlab.be"
LABEL url="https://git.rlab.be/sysadmins/matrix-self-register/"
LABEL version="0.1.0"
LABEL license="GNU GPL v3.0+"

ENV PYTHONUNBUFFERED 1
# Disable breakpoints (shouldn't be any but just in case)
ENV PYTHONBREAKPOINT 0

# Define limited user
ARG APP_USER=app
ARG APP_ROOT=/srv/app
ARG APP_USER_UID=2000
ARG APP_USER_GID=2000

ARG GUNICORN_VERSION=19.9.0
ARG GUNICORN_HASH=sha256:aa8e0b40b4157b36a5df5e599f45c9c76d6af43845ba3b3b0efe2c70473c2471

RUN addgroup -g "${APP_USER_GID}" "${APP_USER}" \
    && adduser \
    -D \
    -h "${APP_ROOT}" \
    -s /sbin/nologin \
    -u "${APP_USER_UID}" \
    -G "${APP_USER}" "${APP_USER}"

# Bring site-packages from previous stage
COPY --from=installer /usr/local/lib/python3.7/site-packages /usr/local/lib/python3.7/site-packages

# Reinstall Gunicorn for it to be present as a local binary
RUN cd /tmp \
    && echo -n > gunicorn_req.txt \
    && echo "gunicorn==${GUNICORN_VERSION} --hash=${GUNICORN_HASH}" >> gunicorn_req.txt \
    && pip install --no-cache-dir --force-reinstall --requirement /tmp/gunicorn_req.txt \
    && rm /tmp/gunicorn_req.txt

WORKDIR "${APP_ROOT}"

# Copy Gunicorn settings
COPY --chown=app:app yog_sothoth/conf/gunicorn.py ./

EXPOSE 8000

# Drop privs
USER ${APP_USER}
CMD ["gunicorn", "--config", "/srv/app/gunicorn.py", "yog_sothoth.app:app"]
