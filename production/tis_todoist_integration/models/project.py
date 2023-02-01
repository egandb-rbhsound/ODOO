# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.

from odoo import api, fields, models
import todoist
import requests
import json


class Project(models.Model):
    _inherit = "project.project"

    todoist_project_id = fields.Char(string='Todoist Project ID')
    last_sync_at = fields.Datetime(string='Last Sync From Todoist At')



class ProjectTask(models.Model):
    _inherit = "project.task"

    todoist_task_id = fields.Char(string='Todoist Task ID')
    priority = fields.Selection([('1', 'Low'), ('2', 'Normal'), ('3', 'High'), ('4', 'Important')], default='1', index=True)
    last_sync_at = fields.Datetime(string='Last Sync From Todoist At')

