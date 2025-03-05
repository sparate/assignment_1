#!/bin/bash

echo " Installing system dependencies..."
sudo apt update && sudo apt install -y python3 python3-pip postgresql postgresql-contrib rabbitmq-server

echo " Installing Python dependencies..."
pip3 install -r requirements.txt

echo " Setting up PostgreSQL database..."
sudo -u postgres psql <<EOF
CREATE DATABASE my_database;
CREATE USER my_user WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE my_database TO my_user;
EOF

echo " Applying database schema..."
psql -U my_user -d my_database -f schema.sql

echo " Starting RabbitMQ..."
sudo systemctl enable rabbitmq-server
sudo systemctl start rabbitmq-server

echo " Installation completed successfully!"


