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
        'views/formative_unit/list.xml',
        'views/formative_unit/form.xml',
        'views/professional_module/list.xml',
        'views/professional_module/form.xml',
        'views/professional_module/report.xml',
        'views/teacher/list.xml',
        'views/teacher/form.xml',
        'views/study/list.xml',
        'views/study/form.xml',
        'views/student/list.xml',
        'views/student/form.xml',
        'views/student/kanban.xml',
        'views/followup/list.xml',
        'views/followup/form.xml',
        'views/level/list.xml',
        'views/level/form.xml',
        'views/classroom/list.xml',
        'views/classroom/form.xml',       
        'views/group/list.xml',
        'views/group/form.xml',
    ],
    'license': 'AGPL-3',
    'application': True,
    
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}