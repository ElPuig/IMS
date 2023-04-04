#!/bin/bash
sudo service odoo stop && sudo -u odoo bash -c 'odoo -d odoo -u ims --stop-after-init -c /etc/odoo/odoo.conf' && sudo service odoo start