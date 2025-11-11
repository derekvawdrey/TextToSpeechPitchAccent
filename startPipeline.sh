#!/bin/bash

set -euo pipefail

REPO_URL="https://github.com/derekvawdrey/OnseiModified.git"
FAST_SPEECH_2_REPO_URL="https://github.com/derekvawdrey/Japanese_FastSpeech2.git"
ONSEI_ROOT="${ONSEI_ROOT:-/Users/derekvawdrey/Workspace/School/CS479FinalProject/onsei}"
FAST_SPEECH_2_ROOT="${FAST_SPEECH_2_ROOT:-/Users/derekvawdrey/Workspace/School/CS479FinalProject/fast-speech-2}"
API_PORT="${API_PORT:-8000}"
CONTAINER_NAME="${CONTAINER_NAME:-onsei-api}"
BASE_IMAGE_TAG="${BASE_IMAGE_TAG:-onsei}"
API_IMAGE_TAG="${API_IMAGE_TAG:-onsei-api}"

ensure_repo() {
  if [ -d "$ONSEI_ROOT/.git" ]; then
    git -C "$ONSEI_ROOT" fetch --prune
  else
    rm -rf "$ONSEI_ROOT"
    git clone "$REPO_URL" "$ONSEI_ROOT"
  fi
}

ensure_fast_speech_2_repo() {
  if [ -d "$FAST_SPEECH_2_ROOT/.git" ]; then
    git -C "$FAST_SPEECH_2_ROOT" fetch --prune
  else
    rm -rf "$FAST_SPEECH_2_ROOT"
    git clone "$FAST_SPEECH_2_REPO_URL" "$FAST_SPEECH_2_ROOT"
  fi
}

build_images() {
  docker build -t "$BASE_IMAGE_TAG" "$ONSEI_ROOT"
  docker build -t "$API_IMAGE_TAG" -f "$ONSEI_ROOT/Dockerfile.api" "$ONSEI_ROOT"
}

restart_api() {
  docker stop "$CONTAINER_NAME" >/dev/null 2>&1 || true
  docker rm "$CONTAINER_NAME" >/dev/null 2>&1 || true

  docker run \
    --name "$CONTAINER_NAME" \
    --restart unless-stopped \
    -d \
    -p "${API_PORT}:8000" \
    "$API_IMAGE_TAG"
}

ensure_repo
ensure_fast_speech_2_repo
build_images
restart_api

echo "onsei API container '${CONTAINER_NAME}' is running on port ${API_PORT}."