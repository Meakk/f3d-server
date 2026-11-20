#!/bin/bash
set -euo pipefail

cd /opt/sweetbot

echo "Fetching latest changes..."
git fetch origin

echo "Updating working tree..."
git reset --hard "$1"

echo "Restarting service..."
sudo systemctl restart sweetbot

echo "Deployment successful!"
