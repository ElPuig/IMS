#!/bin/bash
sudo service odoo stop && sudo -u odoo bash -c 'odoo -d ims -u ims --stop-after-init -c /etc/odoo/odoo.conf' && sudo service odoo start
