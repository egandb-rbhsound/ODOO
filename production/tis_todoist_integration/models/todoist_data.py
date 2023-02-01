# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2019. All rights reserved.

from todoist.api import TodoistAPI

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class TodoistData(models.Model):
    _name = "todoist.data"
    _description = 'Todoist Data'

    def get_todoist_projects(self):
        api_token = self.env.user.todoist_api_token
        if not api_token:
            raise UserError(_('Please Enter Todoist API Token'))
        url = TodoistAPI(api_token)
        url.sync()
        project_details = url.state['projects']
        if project_details:
            for project in project_details:
                if project['parent_id']:
                    raise UserError(_('Does not support child projects or sub projects.'))
                existing_project = self.env['project.project'].search(
                    ['|', ('active', '=', True), ('active', '=', False), ('todoist_project_id', '=', project['id'])])
                if not existing_project:
                    self.env['project.project'].create({'name': project['name'], 'todoist_project_id': project['id'],
                                                        'last_sync_at': fields.Datetime.now()})
                else:
                    existing_project.update({'name': project['name'], 'todoist_project_id': project['id'],
                                             'last_sync_at': fields.Datetime.now()})
                    if project['is_archived']:
                        existing_project.update({'active': False})
                    else:
                        existing_project.update({'active': True})
            self.delete_todoist_projects()
        else:
            raise UserError(_('Please Enter Valid API Token'))

    def get_todoist_tasks(self):
        task = self.env['project.task']
        api_token = self.env.user.todoist_api_token
        url = TodoistAPI(api_token)
        url.sync()
        task_details = url.state['items']
        if task_details:
            for data in task_details:
                project_id = self.env['project.project'].search(['|', ('active', '=', True), ('active', '=', False),
                                                                 ('todoist_project_id', '=', data['project_id'])])
                existing_tasks = task.search(
                    ['|', ('active', '=', True), ('active', '=', False), ('todoist_task_id', '=', data['id'])])
                if not existing_tasks:
                    new_task = task.create({
                        'name': data['content'],
                        'todoist_task_id': data['id'],
                        'project_id': project_id.id,
                        'last_sync_at': fields.Datetime.now()
                    })
                    if data['parent_id']:
                        parent_task = task.search(
                            ['|', ('active', '=', True), ('active', '=', False),
                             ('todoist_task_id', '=', data['parent_id'])])
                        if parent_task.parent_id:
                            raise UserError(_('Supports only single subtask level'))
                        new_task.update({
                            'parent_id': parent_task.id,
                        })
                    if data['due']:
                        new_task.update({
                            'date_deadline': data['due']['date'],
                        })
                    if data['priority']:
                        new_task.update({
                            'priority': str(data['priority']),
                        })
                    if data['date_completed']:
                        new_task.update({
                            'active': False,
                        })
                    else:
                        new_task.update({
                            'active': True,
                        })
                else:
                    existing_tasks.update({
                        'name': data['content'],
                        'todoist_task_id': data['id'],
                        'project_id': project_id.id,
                        'last_sync_at': fields.Datetime.now()
                    })
                    if data['parent_id']:
                        parent_task = task.search(
                            ['|', ('active', '=', True), ('active', '=', False),
                             ('todoist_task_id', '=', data['parent_id'])])
                        if parent_task.parent_id:
                            raise UserError(_('Supports only single subtask level'))
                        existing_tasks.update({
                            'parent_id': parent_task.id,
                        })
                    if data['due']:
                        existing_tasks.update({
                            'date_deadline': data['due']['date'],
                        })
                    if data['priority']:
                        existing_tasks.update({
                            'priority': str(data['priority']),
                        })
                    # if data['date_completed']:
                    #     existing_tasks.update({
                    #         'active': False,
                    #     })
                    # else:
                    #     existing_tasks.update({
                    #         'active': True,
                    #     })
            self.delete_todoist_tasks()
        else:
            raise UserError(_('Please Enter Valid API Token'))

    def delete_todoist_tasks(self):

        odoo_tasks = []
        todoist_tasks = []
        completed_tasks = []
        o_tasks = self.env['project.task'].search(['|', ('active', '=', True), ('active', '=', False)])

        for o_task in o_tasks:
            if o_task.todoist_task_id:
                odoo_tasks.append(o_task.todoist_task_id)

        api_token = self.env.user.todoist_api_token
        url = TodoistAPI(api_token)
        url.sync()
        task_details = url.state['items']

        if task_details:
            for data in task_details:
                todoist_tasks.append(data['id'])
                if data['date_completed'] != None:
                    completed_tasks.append(data['id'])

            for completed_task in completed_tasks:
                if str(completed_task) in odoo_tasks:

                    task_to_complete = self.env['project.task'].search([('todoist_task_id', '=', str(completed_task))])

                    if task_to_complete:
                        stage = self.env.ref("tis_todoist_integration.project_stage_completed")

                        stage.write({'project_ids': [(4, task_to_complete.project_id.id)]})
                        task_to_complete.stage_id = stage.id

            for odoo_task in odoo_tasks:
                if int(odoo_task) not in todoist_tasks:
                    task_to_delete = self.env['project.task'].search([('todoist_task_id', '=', odoo_task)])

                    task_to_delete.unlink()

        else:
            raise UserError(_('Please Enter Valid API Token'))

    def delete_todoist_projects(self):
        odoo_projects = []
        todoist_projects = []
        o_projects = self.env['project.project'].search(['|', ('active', '=', True), ('active', '=', False)])
        for o_project in o_projects:
            if o_project.todoist_project_id:
                odoo_projects.append(o_project.todoist_project_id)
        api_token = self.env.user.todoist_api_token
        url = TodoistAPI(api_token)
        url.sync()
        project_details = url.state['projects']
        if project_details:
            for data in project_details:
                todoist_projects.append(data['id'])
            for odoo_project in odoo_projects:
                if int(odoo_project) not in todoist_projects:
                    project_to_delete = self.env['project.project'].search(
                        ['|', ('active', '=', True), ('active', '=', False), ('todoist_project_id', '=', odoo_project)])
                    project_to_delete.unlink()

        else:
            raise UserError(_('Please Enter Valid API Token'))
