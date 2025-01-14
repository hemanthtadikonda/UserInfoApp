#!/bin/bash

# Update system packages
sudo yum update -y

# Install necessary packages
sudo yum install -y python3-pip git

# Clone the repository if it doesn't already exist
if [ ! -d "UserInfoApp" ]; then
  git clone https://github.com/hemanthtadikonda/UserInfoApp.git
else
  cd UserInfoApp
  git pull origin main # Update the repository if it already exists
  cd ..
fi

# Navigate to the backend directory
cd UserInfoApp/user-info-app-backend || exit

# Install required Python packages
sudo pip3 install -r requirements.txt

# Copy the service file if it doesn't already exist or update it if modified
SERVICE_FILE="/etc/systemd/system/user-info-app.service"
if [ ! -f "$SERVICE_FILE" ] || ! cmp -s service/user-info-app.service "$SERVICE_FILE"; then
  sudo cp service/user-info-app.service "$SERVICE_FILE"
  sudo systemctl daemon-reload
fi

# Enable and start the service
sudo systemctl enable user-info-app
sudo systemctl restart user-info-app
