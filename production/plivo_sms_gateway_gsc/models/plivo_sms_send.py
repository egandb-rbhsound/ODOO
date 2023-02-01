# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.plivo_sms_gateway_gsc.plivo_sms_gateway_gsc_api.plivo_sms_gateway_gsc_api import PlivoSMSAPI

import logging
_logger = logging.getLogger(__name__)


class PlivoSmsSend(models.Model):
    _name = 'plivo.sms.send'
    _description = "Plivo SMS Send"
    _order = 'id DESC'
    
    @api.depends('recipients')
    def _compute_total_recipients(self):
        for sms_id in self:
            if sms_id.send_sms_to == "single_contact":
                sms_id.recipients_count = len(sms_id.partner_id)
            elif sms_id.send_sms_to == "multiple_contacts":
                sms_id.recipients_count = len(sms_id.partner_ids)
            elif sms_id.send_sms_to == "sms_group":
                sms_id.recipients_count = len(sms_id.sms_group_id.recipients)
            else:
                sms_id.recipients_count = 0
                
    def _compute_plivo_response_data(self):
        for sms_id in self:
            sms_id.total_messages = len(sms_id.sms_log_history_ids)
            sms_id.total_successfully_send_messages = len(sms_id.sms_log_history_ids.filtered(lambda x: x.status == "Delivered"))
            sms_id.total_error_messages = len(sms_id.sms_log_history_ids.filtered(lambda x: x.status != "Delivered"))
    
    
    SEND_SMS_TO_SELECTIONS = [
        ('single_contact', 'Contact'),
        ('multiple_contacts', 'Multiple Contacts'),
        ('sms_group', 'SMS Group'),
        ('mobile', 'Mobile'),
    ]
    STATUS_SELECTION = [
        ('draft', 'Draft'),
        ('done', 'Sent'),
    ]
    
    name = fields.Char("SMS ID", help="ID", copy=False)
    plivo_account_id = fields.Many2one("plivo.sms.gateway.account", "SMS Account", domain="[('state', '=', 'confirmed')]", help="SMS Account")
    send_sms_to = fields.Selection(SEND_SMS_TO_SELECTIONS, "Send SMS To", default="single_contact")
    partner_id = fields.Many2one("res.partner", "Contact")
    partner_ids = fields.Many2many("res.partner", "plivo_sms_send_partners_rel", "plivo_sms_send_id", "partner_id", "Contacts")
    sms_group_id = fields.Many2one("plivo.sms.groups", "SMS Group")
    mobile_number = fields.Char("Mobile (With Country Code)", help="Mobile number (With Country Code)")
    message = fields.Text("Message", help="Message")
    recipients_count = fields.Integer(string='recipients Count', compute='_compute_total_recipients')
    recipients = fields.Many2many("res.partner", 'plivo_sms_send_res_partners_rel', 'sms_send_id', 'partner_id',
                                    "Recipients", required=True)
    sms_log_history_ids = fields.One2many("plivo.sms.log.history", "sms_send_rec_id", "SMS Log History")
    total_messages = fields.Integer("Total No. of Messages", compute="_compute_plivo_response_data")
    total_successfully_send_messages = fields.Integer("Total Successfully Send Messages", compute="_compute_plivo_response_data")
    total_error_messages = fields.Integer("Total No. Error Messages", compute="_compute_plivo_response_data")
    state = fields.Selection(STATUS_SELECTION, string="Status", readonly=True, copy=False, default='draft', required=True)
    sms_template_id = fields.Many2one("plivo.sms.template", "SMS Template", domain="[('model_id', '=', False)]", copy=False,)

    # Odoo Logic Section
    # =====================    
    @api.model
    def create(self, vals):
        seq_id = self.env['ir.sequence'].next_by_code('odoo.plivo.sms.send.seq')
        vals.update({'name': seq_id })
        return super(PlivoSmsSend, self).create(vals)
    
    def unlink(self):
        for rec in self:
            if rec.state == "done":
                error_message = _("You can not delete SMS record which is in Sent State.")
                raise UserError(error_message)
    
    @api.onchange("sms_template_id")
    def onchange_sms_template_id(self):
        if self.sms_template_id:
            self.message = self.sms_template_id.message
        else:
            self.message = ""
            
    def action_view_recipients(self):
        """
            :return: action or error
        """
        recipients = []
        if self.send_sms_to == "single_contact":
            recipients = self.env['res.partner'].sudo().search([('id', 'in', self.partner_id.ids)])
        elif self.send_sms_to == "multiple_contacts":
            recipients = self.env['res.partner'].sudo().search([('id', 'in', self.partner_ids.ids)])
        elif self.send_sms_to == "sms_group":
            recipients = self.env['res.partner'].sudo().search([('id', 'in', self.sms_group_id.recipients.ids)])
        
        action = {
            'domain': "[('id', 'in', " + str(recipients.ids) + " )]",
            'name': "Recipients",
            'view_mode': 'tree,form',
            'res_model': 'res.partner',
            'type': 'ir.actions.act_window',
        }
        return action
    
    def send_sms_to_recipients(self, mobile):
        mobile = mobile or ""
        plivo_account_id = self.plivo_account_id
        plivo_sms_log_history_obj = self.env['plivo.sms.log.history']
        data = {
            "src": plivo_account_id.plivo_account_from_mobile_number,
            "dst": mobile,
            'log': plivo_account_id.plivo_log,
            "text": self.message
        }
        PlivoSMSAPIObj = PlivoSMSAPI()
        response_obj = PlivoSMSAPIObj.post_plivo_sms_send_to_recipients_api(plivo_account_id, data, "send_sms")
        if response_obj.status_code in [202]:
            response = response_obj.json()
            plivo_sms_log_history_obj.create({
                'sms_send_rec_id': self.id,
                'plivo_account_id': plivo_account_id.id,
                'mobile_number': mobile,
                'message_id': response.get("message_uuid")[0],
                'message': self.message,
                'status': "Delivered",
            })
        elif response_obj.status_code == 401:
            plivo_sms_log_history_obj.create({
                'sms_send_rec_id': self.id,
                'plivo_account_id': plivo_account_id.id,
                'mobile_number': mobile,
                'message_id': "",
                'message': "Authentication failed.\nResponse Status Code: %s.\nError Response: %s" % (response_obj.status_code, response_obj.text),
                'status': "failed",
            })
        elif response_obj.status_code == 400:
            response = response_obj.json()
            plivo_sms_log_history_obj.create({
                'sms_send_rec_id': self.id,
                'plivo_account_id': plivo_account_id.id,
                'mobile_number': mobile,
                'message_id': "",
                'message': "A parameter is missing or is invalid.\nResponse Status Code: %s.\nError Response: %s" % (response_obj.status_code, response.get('error')),
                'status': "failed",
            })
        else:
            plivo_sms_log_history_obj.create({
                'sms_send_rec_id': self.id,
                'plivo_account_id': plivo_account_id.id,
                'mobile_number': mobile,
                'message_id': "",
                'message': "A parameter is missing or is invalid.\nError Response: %s" % (response_obj.text),
                'status': "failed",
            })
        return True
    
    def action_send_sms_to_recipients(self):
        send_sms_to = self.send_sms_to
        error_message = ""
        if not self.plivo_account_id:
            error_message = _("SMS Account is required so select SMS Account and try again to Send Message.")
            raise UserError(error_message)
        if not send_sms_to:
            error_message = _("Send SMS To is required so select Send SMS To and try again to Send Message.")
            raise UserError(error_message)
        
        if self.send_sms_to == "single_contact":
            self.send_sms_to_recipients(self.partner_id.mobile)
        elif self.send_sms_to == "multiple_contacts":
            for partner_id in self.partner_ids:
                self.send_sms_to_recipients(partner_id.mobile)
        elif self.send_sms_to == "sms_group":
            for partner_id in self.sms_group_id.recipients:
                self.send_sms_to_recipients(partner_id.mobile)
        elif self.mobile_number:
            self.send_sms_to_recipients(self.mobile_number)
        self.write({
                'state': 'done',
        })
        return True
