# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class PlivoSMSLogHistory(models.Model):
    _name = 'plivo.sms.log.history'
    _description = "Plivo SMS Log History"
    _order = 'id DESC'
    
    name = fields.Char("Log ID", copy=False, help="LOG ID")
    sms_send_rec_id =  fields.Many2one("plivo.sms.send", "SMS Send ID", copy=False)
    plivo_account_id = fields.Many2one("plivo.sms.gateway.account", "SMS Account ID", copy=False)
    partner_id = fields.Many2one("res.partner", "Contact", copy=False)
    mobile_number = fields.Char("Mobile No.", copy=False)
    message_id = fields.Char("Message ID", copy=False)
    message = fields.Text("Message", copy=False)
    status = fields.Char("Status", copy=False)
    
    @api.model
    def create(self, vals):
        seq_id = self.env['ir.sequence'].next_by_code('odoo.plivo.sms.log.history.seq')
        vals.update({'name': seq_id })
        return super(PlivoSMSLogHistory, self).create(vals)
    
    