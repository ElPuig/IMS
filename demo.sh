#!/bin/bash
echo "Installing the IMS (with demo data)..."
sudo service odoo stop
pip3 install phonenumbers
sudo -u odoo bash -c 'odoo -d ims --stop-after-init -i ims -c /etc/odoo/odoo.conf'
sudo service odoo start
echo "Done!"
