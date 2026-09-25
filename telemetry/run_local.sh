#!/bin/bash
set -e
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
# En Arch/Omarchy el serial pertenece a uucp. Conserva el grupo ya autorizado.
if id -nG | tr ' ' '\n' | grep -qx uucp; then
  exec /usr/bin/python3 run_local.py
elif id -nG "$(id -un)" | tr ' ' '\n' | grep -qx uucp; then
  exec newgrp uucp <<'SCRIPT'
exec /usr/bin/python3 run_local.py
SCRIPT
else
  exec /usr/bin/python3 run_local.py
fi
