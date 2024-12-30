#!/bin/bash
echo "Updating the IMS..."
sudo service odoo stop
sudo -u odoo bash -c 'odoo -d ims -u ims --stop-after-init -c /etc/odoo/odoo.conf --dev=all'
sudo service odoo start
