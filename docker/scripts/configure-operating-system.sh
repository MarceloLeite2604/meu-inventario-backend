#!/bin/sh

set -eu

echo "Executing script \"$0\"."

if [ -z "${CONTAINER_UID:-}" ]; then
    echo "Error: CONTAINER_UID environment variable is not set."
    exit 1
fi

if [ -z "${CONTAINER_GID:-}" ]; then
    echo "Error: CONTAINER_GID environment variable is not set."
    exit 1
fi

if [ -z "${CONTAINER_USERNAME:-}" ]; then
    echo "Error: CONTAINER_USERNAME environment variable is not set."
    exit 1
fi

if [ -z "${MNZ_PB_WORK_DIRECTORY:-}" ]; then
    echo "Error: MNZ_PB_WORK_DIRECTORY environment variable is not set."
    exit 1
fi

SKIP_BUILD_DEPS="${1:-false}"

if [ "$SKIP_BUILD_DEPS" != "true" ]; then
    packages_to_install="build-base linux-headers"

    echo "Updating package list and installing required packages..."
    apk update
    for package in $packages_to_install; do
        if ! apk info -e "$package" >/dev/null 2>&1; then
            echo "Installing package: $package"
            apk add "$package"
        else
            echo "Package $package is already installed."
        fi
    done
else
    echo "Skipping build dependencies installation (runtime stage)."
fi

echo "Creating user and group for the application..."
if ! getent group "$CONTAINER_GID" >/dev/null 2>&1; then
    addgroup -g "$CONTAINER_GID" "$CONTAINER_USERNAME";
else
    EXISTING_GROUP=$(getent group "$CONTAINER_GID" | cut -d: -f1);
    echo "Group with GID $CONTAINER_GID already exists: $EXISTING_GROUP";
fi

if ! getent passwd "$CONTAINER_UID" >/dev/null 2>&1; then
    adduser -D \
        -u "$CONTAINER_UID" \
        -G "$CONTAINER_USERNAME" \
        -h "/home/$CONTAINER_USERNAME" \
        -s /bin/sh "$CONTAINER_USERNAME";
else
    EXISTING_USER=$(getent passwd "$CONTAINER_UID" | cut -d: -f1);
    echo "User with UID $CONTAINER_UID already exists: $EXISTING_USER";
fi

echo "Creating working directory and setting permissions..."
mkdir -p "$MNZ_PB_WORK_DIRECTORY"
chown -R "$CONTAINER_USERNAME:$CONTAINER_USERNAME" "$MNZ_PB_WORK_DIRECTORY"

echo "Setting umask to 0002 for all users..."
printf '%s\n' 'umask 0002' > /etc/profile.d/umask.sh && \
chmod 644 /etc/profile.d/umask.sh

echo "Script \"$0\" completed successfully."
