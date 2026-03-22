#!/usr/bin/env bash

set -heu

echo "==============>> container-webview API starting"
echo "==============>> run $*"
exec "$@"
