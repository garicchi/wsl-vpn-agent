#!/bin/bash -e

SCRIPT_PATH="$(cd $(dirname $0); pwd)"

UNIT="wsl-vpn-agent"

apt install python3
mkdir -p /opt/${UNIT}
cp ${SCRIPT_PATH}/main.py /opt/${UNIT}

systemctl enable ${SCRIPT_PATH}/${UNIT}.service
systemctl start ${UNIT}.service

echo "success!"