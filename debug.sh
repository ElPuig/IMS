#!/bin/bash
echo "Starting the IMS [DEBUG MODE]..."
sudo service odoo stop
sudo -u odoo bash -c 'odoo -d ims --stop-after-init -c /etc/odoo/odoo.conf --dev=all'
sudo service odoo start