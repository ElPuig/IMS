#!/bin/bash
echo "Installing the IMS..."
sudo service odoo stop
sudo -u odoo bash -c 'odoo -d ims -i ims --stop-after-init -c /etc/odoo/odoo.conf'
sudo service odoo start
echo "Done!"
