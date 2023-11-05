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
    # only 'base_setup', 'hr', 'auth_oauth' are needed. The rest are installed sometimes (and sometimes nor) and I don't know why, so I decided to install all manyally in order to avoid errors.
    'depends': ['base_setup', 'hr', 'hr_org_chart', 'auth_oauth', 'contacts', 'project', 'mass_mailing', 'survey'],

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

        'views/employees/employee/kanban.xml',
        'views/employees/employee/list.xml',
        'views/employees/employee/form.xml',

        'views/contacts/contact/list.xml',
        'views/contacts/contact/form.xml',

        'views/employees/job/list.xml',
        'views/employees/job/form.xml',
        
        'views/people/tracking/list.xml',
        'views/people/tracking/form.xml',
        'views/people/provider/list.xml',
        'views/people/provider/form.xml',
        'views/people/provider/kanban.xml',

        'views/facilities/classroom/list.xml',
        'views/facilities/classroom/form.xml',       

        'views/contacts/group/list.xml',
        'views/contacts/group/form.xml',        
        'views/employees/role/list.xml',
        'views/employees/role/form.xml',
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

        'demo/contacts/group.xml',
        'demo/organization/teaching.xml',   
        'demo/organization/company.xml',           
        
        'demo/employees/job.xml',
        'demo/employees/department.xml',
        'demo/employees/work_location.xml',
        'demo/employees/teacher.xml',
        'demo/employees/pas.xml',
        'demo/employees/role.xml', 
        'demo/employees/employee.xml',   

        'demo/contacts/student.xml',   
        'demo/contacts/provider.xml',         
    ],   
    'assets': {       
        'web.assets_backend': [
            'ims/static/src/fields/*',
        ],
    },
}
