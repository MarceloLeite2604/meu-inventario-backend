ARG PYTHON_VERSION=3.13.5-alpine
ARG HOST_UID=1000
ARG HOST_GID=1000
ARG HOST_USERNAME=appuser
ARG MNZ_MI_WORK_DIRECTORY

FROM python:$PYTHON_VERSION AS builder

ARG HOST_UID
ARG HOST_GID
ARG HOST_USERNAME
ARG MNZ_MI_WORK_DIRECTORY

ENV CONTAINER_UID=$HOST_UID
ENV CONTAINER_GID=$HOST_GID
ENV CONTAINER_USERNAME=$HOST_USERNAME
ENV VIRTUAL_ENV="$MNZ_MI_WORK_DIRECTORY/.venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app/build

COPY --chown=$CONTAINER_USERNAME:$CONTAINER_USERNAME \
    ./docker/scripts/configure-operating-system.sh \
    .

RUN --mount=type=cache,target=/var/cache/apk,sharing=locked,id=apk-cache,uid=0,gid=0 \
    chmod +x ./configure-operating-system.sh && \
    ./configure-operating-system.sh && \
    rm ./configure-operating-system.sh

RUN mkdir -p "$MNZ_MI_WORK_DIRECTORY"

COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /usr/local/bin/

WORKDIR "$MNZ_MI_WORK_DIRECTORY"

COPY --chown=$CONTAINER_USERNAME:$CONTAINER_USERNAME requirements.txt ./

USER "$CONTAINER_USERNAME"

RUN --mount=type=cache,target="/home/$CONTAINER_USERNAME/.cache/uv",id=uv-cache,uid="$CONTAINER_UID",gid="$CONTAINER_GID" \
    uv venv && \
    UV_CACHE_DIR="/home/$CONTAINER_USERNAME/.cache/uv" \
    UV_LINK_MODE=copy \
    uv pip install -r requirements.txt

FROM python:$PYTHON_VERSION

ARG HOST_UID
ARG HOST_GID
ARG HOST_USERNAME
ARG MNZ_MI_WORK_DIRECTORY

ENV CONTAINER_UID=$HOST_UID
ENV CONTAINER_GID=$HOST_GID
ENV CONTAINER_USERNAME=$HOST_USERNAME
ENV MNZ_MI_WORK_DIRECTORY="$MNZ_MI_WORK_DIRECTORY"
ENV VIRTUAL_ENV="$MNZ_MI_WORK_DIRECTORY/.venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY --chown=$CONTAINER_USERNAME:$CONTAINER_USERNAME \
    ./docker/scripts/configure-operating-system.sh \
    .

RUN --mount=type=cache,target=/var/cache/apk,sharing=locked,id=apk-cache,uid=0,gid=0 \
    chmod +x ./configure-operating-system.sh && \
    ./configure-operating-system.sh true && \
    rm ./configure-operating-system.sh

USER "$CONTAINER_USERNAME"

WORKDIR "$MNZ_MI_WORK_DIRECTORY"

COPY --from=builder --chown=$CONTAINER_USERNAME:$CONTAINER_USERNAME "$MNZ_MI_WORK_DIRECTORY" "$MNZ_MI_WORK_DIRECTORY"

COPY --chown=$CONTAINER_USERNAME:$CONTAINER_USERNAME ./docker/scripts/entrypoint.sh .

RUN chmod +x ./entrypoint.sh

COPY --chown=$CONTAINER_USERNAME:$CONTAINER_USERNAME ./src ./src
COPY --chown=$CONTAINER_USERNAME:$CONTAINER_USERNAME ./database ./database
COPY --chown=$CONTAINER_USERNAME:$CONTAINER_USERNAME .env* .

ENTRYPOINT ["sh", "./entrypoint.sh"]
