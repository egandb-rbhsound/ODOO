# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.

from odoo import api, fields, models, _
import requests
from odoo.exceptions import ValidationError, UserError
import json


class ResUsers(models.Model):
    _inherit = 'res.users'

    todoist_api_token = fields.Char(string='Todoist API Token')

    def get_todoist_api_token(self):
        url_action = {
            'type': 'ir.actions.act_url',
            'name': "Todoist API Token",
            'target': 'new',
            'url': 'https://todoist.com/prefs/integrations',
        }
        return url_action

    def sync_with_todoist(self):
        todoist_data = self.env['todoist.data']
        todoist_data.get_todoist_projects()
        todoist_data.get_todoist_tasks()
        return {'name': 'Success Message',
                'type': 'ir.actions.act_window',
                'res_model': 'sync.wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new'}

