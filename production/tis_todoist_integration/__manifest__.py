# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.

{
    'name': 'Todoist - Odoo Integration',
    'version': '14.0.0.2',
    'category': 'Project',
    'sequence': 1,
    'author': 'Technaureus Info Solutions Pvt. Ltd.',
    'summary': 'Todoist - Odoo Integration',
    'website': 'http://www.technaureus.com/',
    'price': 49,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'description': """ 
    Integrating Todoist with Odoo and managing tasks from Todoist to Odoo.
""",
    'depends': ['project'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_users_views.xml',
        'views/project_views.xml',
        'wizard/notification_wizard_view.xml',
        'data/data.xml'
    ],
    'demo': [
    ],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
