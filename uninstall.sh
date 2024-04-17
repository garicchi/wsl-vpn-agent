#!/bin/bash -e

SCRIPT_PATH="$(cd $(dirname $0); pwd)"

UNIT="wsl-vpn-agent"

rm -rf /opt/${UNIT}
systemctl stop ${UNIT}.service
systemctl disable ${SCRIPT_PATH}/${UNIT}.service
systemctl daemon-reload
systemctl reset-failed

echo "success!"