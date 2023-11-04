#!/bin/bash
echo "Installing the IMS..."
sudo service odoo stop
pip3 install phonenumbers
sudo -u odoo bash -c 'odoo -d ims --stop-after-init -i ims -c /etc/odoo/odoo.conf --without-demo=WITHOUT_DEMO'
sudo service odoo start
echo "Done!"
