## NETWORK_SECURITY PROJECT for Phishing Data

Docker Setup In EC2 commands to be Executed
#option al

sudo apt-get update -y

sudo apt-get upgrade

#required

curl -fsSL https://get.docker.com -o get-docker.sh

sudo sh get-docker.sh

sudo usermod -aG docker ubuntu

newgrp docker