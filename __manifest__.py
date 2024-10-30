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
    'version': '0.13.0',

    # any module necessary for this one to work correctly
    # only 'base_setup', 'hr', 'auth_oauth' are needed. The rest are installed sometimes (and sometimes nor) and I don't know why, so I decided to install all manyally in order to avoid errors.
    'depends': ['base_setup', 'hr', 'hr_org_chart', 'auth_oauth', 'contacts', 'project', 'mass_mailing', 'survey'],

    # always loaded
   'data': [
        'security/groups.xml',        
        'security/ir.model.access.csv',                        
        
        'views/settings/form.xml',
        'views/settings/menu.xml',        

        'views/curriculum/menu.xml',

        'views/curriculum/subject/list.xml',
        'views/curriculum/subject/form.xml',
        'views/curriculum/subject/menu.xml',

        'views/curriculum/study/list.xml',
        'views/curriculum/study/form.xml',     
        'views/curriculum/study/menu.xml',        
        
        'views/curriculum/level/list.xml',
        'views/curriculum/level/form.xml',
        'views/curriculum/level/menu.xml',

        'views/people/employee/kanban.xml',        
        'views/people/employee/list.xml',
        'views/people/employee/form.xml',       
        'views/people/employee/menu.xml',       

        'views/employees/job/list.xml',
        'views/employees/job/form.xml',        

        'views/employees/tracking/list.xml',
        'views/employees/tracking/form.xml',  
        'views/employees/tracking/menu.xml',     

        'views/people/workgroup/list.xml',
        'views/people/workgroup/form.xml',  
        'views/people/workgroup/menu.xml',  

        'views/people/menu.xml',  
        'views/people/contact/list.xml',
        'views/people/contact/form.xml',
        'views/people/contact/search.xml',
        'views/people/contact/kanban.xml',
        'views/people/contact/menu.xml',
        'views/people/group/list.xml',
        'views/people/group/form.xml',  
        'views/people/group/menu.xml',      

        'views/facilities/menu.xml',

        'views/facilities/space/list.xml',
        'views/facilities/space/form.xml',
        'views/facilities/space/search.xml',
        'views/facilities/space/menu.xml',

        'views/facilities/space_type/list.xml',
        'views/facilities/space_type/form.xml',
        'views/facilities/space_type/menu.xml',       

        'views/employees/role/list.xml',
        'views/employees/role/form.xml',
        'views/employees/role/menu.xml',

        'views/attendance/menu.xml',

        'views/attendance/attendance_template/menu.xml',
        'views/attendance/attendance_template/list.xml',
        'views/attendance/attendance_template/form.xml',
        'views/attendance/attendance_session/list.xml',
        'views/attendance/attendance_session/form.xml',
        'views/attendance/attendance_session/calendar.xml',
        'views/attendance/attendance_session/menu.xml',
        'views/attendance/attendance_status/list.xml',
        'views/attendance/attendance_status/form.xml',
        'views/attendance/attendance_status/menu.xml',       
        
        'views/documentation/menu.xml',       
        'views/documentation/minutes/menu.xml',       
        'views/documentation/minutes/list.xml',       
        'views/documentation/minutes/form.xml',   
        
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    
    # only loaded in demonstration mode (only loaded when installed, ignored when updated)
    'demo': [
        # this order is needed due dependencies
        'demo/curriculum/level.xml',
        'demo/curriculum/study.xml',
        'demo/curriculum/subject.xml',

        'demo/facilities/space_type.xml',         
        'demo/facilities/space.xml',         

        'demo/contacts/group.xml',        
        'demo/contacts/company.xml',        
        
        'demo/employees/teaching.xml',   
        'demo/employees/job.xml',
        'demo/employees/department.xml',
        'demo/employees/work_location.xml',
        'demo/employees/teacher.xml',
        'demo/employees/pas.xml',
        'demo/employees/role.xml', 
        'demo/employees/employee.xml',  
        'demo/employees/workgroup.xml',   

        'demo/contacts/student.xml',
        'demo/contacts/provider.xml',
        'demo/contacts/enrollment.xml',

        'demo/attendance/attendance_template.xml',
        'demo/attendance/attendance_schedule.xml',
        'demo/attendance/attendance_session.xml',
        'demo/attendance/attendance_status.xml',
    ],   
    'assets': {       
        'web.assets_backend': [
            'ims/static/src/fields/*',
        ],
    },
}
