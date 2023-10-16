# -*- coding: utf-8 -*-
{
    'name': "IMS: Institute Management System",

    'summary': """
        Provides a free, open-source, comprehensive and intuitive environment in order to manage an educational center.
    """,

    'description': """
        The IMS's main objective is to provide a free, open-source, comprehensive and intuitive environment in order to manage an educational center. To achieve that, a group of bold teachers from 'Institut Puig Castellar' (Santa Coloma de Gramenet, Barcelona, Spain) is developing this Odoo module as part of the Quality and Continuous Improvement Project (Q&CIP or PQiMC in our local language: Catalan).
    """,

    'author': "El Puig",
    'website': "https://github.com/ElPuig/IMS",
    #icon authory: thanks to Memed_Nurrohmad (https://pixabay.com/es/vectors/sombrero-graduaci%C3%B3n-gorra-educaci%C3%B3n-1674894/)

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Educational',
    'version': '0.4.0',

    # any module necessary for this one to work correctly
    'depends': ['base_setup'],

    # always loaded
   'data': [
        'security/ir.model.access.csv',

        'views/settings/form.xml',

        'views/menu.xml',

        'views/formative_unit/list.xml',
        'views/formative_unit/form.xml',

        'views/professional_module/list.xml',
        'views/professional_module/form.xml',
        'views/professional_module/report.xml',

        'views/person/list.xml',
        'views/person/form.xml',
        'views/person/kanban.xml',

        'views/corporate_person/list.xml',
        'views/corporate_person/form.xml',
        'views/corporate_person/kanban.xml',

        'views/administrative/list.xml',
        'views/administrative/form.xml',
        'views/administrative/kanban.xml',

        'views/teacher/list.xml',
        'views/teacher/form.xml',
        'views/teacher/kanban.xml',
        
        'views/student/list.xml',
        'views/student/form.xml',
        'views/student/kanban.xml',

        'views/study/list.xml',
        'views/study/form.xml',            

        'views/tracking/list.xml',
        'views/tracking/form.xml',

        'views/level/list.xml',
        'views/level/form.xml',

        'views/classroom/list.xml',
        'views/classroom/form.xml',       

        'views/group/list.xml',
        'views/group/form.xml',

        'views/teacher_position/list.xml',
        'views/teacher_position/form.xml',

        'views/attendance_template/list.xml',
        'views/attendance_template/form.xml',
        'views/attendance_group/list.xml',
        'views/attendance_group/form.xml',
        'views/attendance_session/list.xml',
        'views/attendance_session/form.xml',
        'views/attendance_status/list.xml',
        'views/attendance_status/form.xml',       
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    
    # only loaded in demonstration mode (only loaded when installed, ignored when updated)
    'demo': [
        'demo/level.xml',
        'demo/classroom.xml',
        'demo/study.xml',
        'demo/professional_module.xml',
        'demo/formative_unit.xml',
        'demo/teacher.xml',
        'demo/group.xml',        
        'demo/teaching.xml',
    ],
}
