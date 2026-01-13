#!/bin/bash
set -e

# Update system
apt-get update
apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Add ubuntu user to docker group
usermod -aG docker ubuntu

# Enable Docker service
systemctl enable docker
systemctl start docker

# Create application directory
mkdir -p /opt/edu-vexxel
chown ubuntu:ubuntu /opt/edu-vexxel

# Create directory for PostgreSQL data
mkdir -p /opt/edu-vexxel/postgres-data
chown -R 999:999 /opt/edu-vexxel/postgres-data

# Create directory for backups
mkdir -p /opt/edu-vexxel/backups
chown ubuntu:ubuntu /opt/edu-vexxel/backups

# Install useful tools
apt-get install -y git htop curl wget

echo "Bootstrap completed successfully"
