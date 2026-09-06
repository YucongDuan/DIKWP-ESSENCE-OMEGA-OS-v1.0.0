#!/usr/bin/env sh
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PYTHONPATH="$HERE/src" python -m essence_omega_os suite --examples "$HERE/examples" --output "$HERE/outputs/reference"
