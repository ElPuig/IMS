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
        
        'views/menu.xml',

        'views/settings/form.xml',
        'views/settings/menu.xml',                                    
        
        'views/community/menu.xml',  
            'views/community/configuration/menu.xml',            

            'views/community/employee/menu.xml', 
            'views/community/employee/kanban.xml',        
            'views/community/employee/list.xml',
            'views/community/employee/form.xml',                                      

            'views/community/workgroup/list.xml',
            'views/community/workgroup/form.xml',  
            'views/community/workgroup/menu.xml',  
            
            'views/community/contact/list.xml',
            'views/community/contact/form.xml',
            'views/community/contact/search.xml',
            'views/community/contact/kanban.xml',
            'views/community/contact/menu.xml',

            'views/community/group/list.xml',
            'views/community/group/form.xml',  
            'views/community/group/menu.xml',    

            'views/community/job/list.xml',
            'views/community/job/form.xml', 
            'views/community/job/menu.xml',    

            'views/community/role/list.xml',
            'views/community/role/form.xml',
            'views/community/role/menu.xml',
                
            'views/community/department/menu.xml',
            'views/community/worklocation/menu.xml',
            'views/community/employmenttypes/menu.xml',

            'views/community/curriculum/subject/list.xml',
            'views/community/curriculum/subject/form.xml',
            'views/community/curriculum/subject/menu.xml',

            'views/community/curriculum/study/list.xml',
            'views/community/curriculum/study/form.xml',     
            'views/community/curriculum/study/menu.xml',        
        
            'views/community/curriculum/level/list.xml',
            'views/community/curriculum/level/form.xml',
            'views/community/curriculum/level/menu.xml',   

            'views/community/facilities/menu.xml',

            'views/community/facilities/space/list.xml',
            'views/community/facilities/space/form.xml',
            'views/community/facilities/space/search.xml',

            'views/community/facilities/space_type/list.xml',
            'views/community/facilities/space_type/form.xml',
            'views/community/facilities/space_type/menu.xml',    

        # 'views/community/tracking/list.xml',
        # 'views/community/tracking/form.xml',  
        # 'views/community/tracking/menu.xml',     

                   

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
