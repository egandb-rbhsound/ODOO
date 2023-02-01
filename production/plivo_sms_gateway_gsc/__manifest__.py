# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#################################################################################
# Author      : Grow Consultancy Services (<https://www.growconsultancyservices.com/>)
# Copyright(c): 2021-Present Grow Consultancy Services
# All Rights Reserved.
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
#################################################################################
{
    # Application Information
    'name': 'Odoo Plivo SMS Gateway',
    'version': '15.1.0',
    'category': 'Tools',
    'license': 'OPL-1',
    
    'summary': """
        Odoo Plivo SMS Gateway helps you integrate & manage Plivo Acct. operations from Odoo. These apps Save your time, Resources, Effort, and Avoid manually manage multiple Plivo Acct(s) to boost your business marketing with this connector.
    """,
    'description': """
        Odoo Plivo SMS Gateway helps you integrate & manage Plivo Account operations from Odoo. These apps Save your time, Resources, Effort, and Avoid manually manage multiple Plivo Accounts to boost your business marketing with this connector.
    """,
    
    # Author Information
    'author': 'Grow Consultancy Services',
    'maintainer': 'Grow Consultancy Services',
    'website': 'http://www.growconsultancyservices.com',
    
    # Application Price Information
    'price': 50,
    'currency': 'EUR',

    # Dependencies
    'depends': ['base', 'mail', 'sale_management', 'stock'],
    
    # Views
    'data': [ 
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/plivo_sms_account_view.xml',
        'views/plivo_sms_groups_view.xml',
        'data/ir_sequence.xml',
        'wizard/plivo_sms_template_preview_views.xml',
        'views/plivo_sms_template_view.xml',
        'views/plivo_sms_send_view.xml',
        'views/plivo_sms_log_history.xml',
        #'views/'
        # wizard/
    ],
    
    # Application Main Image    
    'images': ['static/description/app_profile_image.jpg'],

    # Technical
    'installable': True,
    'application' : True,
    'auto_install': False,
    'active': False,
}
