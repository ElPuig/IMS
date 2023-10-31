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
    'version': '0.9.0',

    # any module necessary for this one to work correctly
    'depends': ['base_setup', 'auth_oauth'],

    # always loaded
   'data': [
        'security/groups.xml',        
        'security/ir.model.access.csv',        

        'templates/form_with_photo.xml',

        'views/settings/form.xml',

        'views/menu.xml',

        'views/curriculum/formative_unit/list.xml',
        'views/curriculum/formative_unit/form.xml',
        'views/curriculum/professional_module/list.xml',
        'views/curriculum/professional_module/form.xml',
        'views/curriculum/professional_module/report.xml',
        'views/curriculum/study/list.xml',
        'views/curriculum/study/form.xml',        
        'views/curriculum/level/list.xml',
        'views/curriculum/level/form.xml',

        'views/people/person/list.xml',
        'views/people/person/form.xml',
        'views/people/person/kanban.xml',
        'views/people/corporate_person/list.xml',
        'views/people/corporate_person/form.xml',
        'views/people/corporate_person/kanban.xml',
        'views/people/administrative/list.xml',
        'views/people/administrative/form.xml',
        'views/people/administrative/kanban.xml',
        'views/people/teacher/list.xml',
        'views/people/teacher/form.xml',
        'views/people/teacher/kanban.xml',
        'views/people/student/list.xml',
        'views/people/student/form.xml',
        'views/people/student/kanban.xml',
        'views/people/tracking/list.xml',
        'views/people/tracking/form.xml',
        'views/people/provider/list.xml',
        'views/people/provider/form.xml',
        'views/people/provider/kanban.xml',

        'views/facilities/classroom/list.xml',
        'views/facilities/classroom/form.xml',       

        'views/organization/student_group/list.xml',
        'views/organization/student_group/form.xml',
        'views/organization/administrative_role/list.xml',
        'views/organization/administrative_role/form.xml',
        'views/organization/teacher_role/list.xml',
        'views/organization/teacher_role/form.xml',
        'views/organization/company/list.xml',
        'views/organization/company/form.xml',
        'views/organization/company/kanban.xml',

        'views/attendance/attendance_template/list.xml',
        'views/attendance/attendance_template/form.xml',
        'views/attendance/attendance_group/list.xml',
        'views/attendance/attendance_group/form.xml',
        'views/attendance/attendance_session/list.xml',
        'views/attendance/attendance_session/form.xml',
        'views/attendance/attendance_status/list.xml',
        'views/attendance/attendance_status/form.xml',       
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    
    # only loaded in demonstration mode (only loaded when installed, ignored when updated)
    'demo': [
        # this order is needed due dependencies
        'demo/curriculum/level.xml',
        'demo/curriculum/study.xml',
        'demo/curriculum/professional_module.xml',
        'demo/curriculum/formative_unit.xml',

        'demo/facilities/classroom.xml',
        
        'demo/organization/administrative_role.xml',

        'demo/people/administrative.xml',        
        'demo/people/teacher.xml',

        'demo/organization/student_group.xml',
        'demo/organization/teaching.xml',   
        'demo/organization/teacher_role.xml',   
        'demo/organization/company.xml',   

        'demo/people/provider.xml',
        'demo/people/student.xml',
    ],   
}
