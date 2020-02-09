Provisioning a new site 
========================

## Required packages:
* nginx
* Python3.6
* virtualenv + pip
* Git

eg, on ubuntu:
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y nginx git python36 python36-venv
```

## Nginx Virtual Host config
* see nginx.template.conf
* replace `DOMAIN` with, e.g, staging.my-domain.com

## Systemd service
* see gunicorn-systemd.template.service
* replace `DOMAIN` with, e.g, staging.my-domain.com

