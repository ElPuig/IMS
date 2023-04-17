# -*- coding: utf-8 -*-
{
    'name': "IMS: Institute Management System",

    'summary': """
        Proporciona un entorn lliure, gratuït i intuïtiu amb el qual sigui possible la gestió integral d'un centre educatiu.        
    """,

    'description': """
        L'objectiu de l'IMS és proporcionar un entorn lliure, gratuït i intuïtiu amb el qual sigui possible la gestió integral d'un centre educatiu.
        La solució consisteix en un conjunt de mòduls per a Odoo, un ERP lliure i totalment configurable, que estan sent desenvolupats per un grup de professors de l'Institut Puig Castellar de Santa Coloma de Gramenet.
    """,

    'author': "El Puig",
    'website': "https://github.com/ElPuig/IMS",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
   'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/uf/list.xml',
        'views/uf/form.xml',
        'views/mp/list.xml',
        'views/mp/form.xml',
        'views/mp/report.xml',
        'views/teacher/list.xml',
        'views/teacher/form.xml',
        'views/study/list.xml',
        'views/study/form.xml',
        'views/student/list.xml',
        'views/student/form.xml',
        'views/follow/list.xml',
        'views/follow/form.xml',
        'views/level/list.xml',
        'views/level/form.xml',
        'views/classroom/list.xml',
        'views/classroom/form.xml',
        'views/status/list.xml',
        'views/status/form.xml',
        'views/student_group/list.xml',
        'views/student_group/form.xml',
    ],
    'license': 'AGPL-3',
    'application': True,
    
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
