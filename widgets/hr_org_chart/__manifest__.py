# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Source: https://github.com/odoo/odoo/blob/16.0/addons/hr_org_chart

#TODO:  should use the employee roles instead of job positions. Multiple roles should be separated by comma (get string from model method)
#       replace hr_org by ims_org
#       this module should be installed also, so all the data must be copied to the "./../"" path.
{
    'name': 'IMS\'s Employee Org Chart',
    'category': 'Hidden',
    'version': '1.0',
    'description':
        """
IMS's Employee Org Chart Widget for HR
=======================

This module extend the employee form with a organizational chart.
(N+1, N+2, direct subordinates)
        """,
    'depends': ['hr', 'ims'],
    'auto_install': True,
    'data': [
        'views/hr_views.xml'
    ],
    'assets': {
        'web._assets_primary_variables': [
            'hr_org_chart/static/src/scss/variables.scss',
        ],
        'web.assets_backend': [
            'hr_org_chart/static/src/fields/*',
        ],
        'web.qunit_suite_tests': [
            'hr_org_chart/static/tests/**/*',
        ],
    },
    'license': 'LGPL-3',
}
