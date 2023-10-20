#!/bin/bash
echo "Removing the IMS..."
sudo service odoo stop
sudo -u odoo bash -c 'dropdb ims'
sudo service odoo start
echo "Done!"
