# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.plivo_sms_gateway_gsc.plivo_sms_gateway_gsc_api.plivo_sms_gateway_gsc_api import PlivoSMSAPI

import logging
_logger = logging.getLogger(__name__)


class PlivoSmsGatewayAccount(models.Model):
    _name = 'plivo.sms.gateway.account'
    _description = "Plivo SMS Gateway SMS"
    
    def _compute_total_sms_data(self):
        plivo_sms_send_obj = self.env['plivo.sms.send']
        plivo_sms_log_history_obj = self.env['plivo.sms.log.history']
        for plivo_account in self:
            plivo_account.sms_records_count = len(plivo_sms_send_obj.search([('plivo_account_id', '=', plivo_account.id)]))
            plivo_account.account_sms_logs_count = len(plivo_sms_log_history_obj.search([('plivo_account_id', '=', plivo_account.id)]))
    
    name = fields.Char("Account Name", help="Account name", required=True, copy=False)
    test_connection_mobile_number = fields.Char("Test Connection Mobile Number", help="Mobile number should be with country code i.e +91xxxxxxxx")
    state = fields.Selection([
        ('new', 'New'),
        ('confirmed', 'Confirmed'),
    ], default='new', help="State")
    
    plivo_auth_id = fields.Char("Auth ID", help="Auth ID", required=True, copy=False)
    plivo_auth_token = fields.Char("Auth Token", help="Auth Token", required=True, copy=False)
    plivo_account_from_mobile_number = fields.Char("From Mobile Number", help="Mobile number should be with country code.", required=True, copy=False)
    plivo_account_type = fields.Char("Account Type", copy=False)
    plivo_auto_recharge = fields.Boolean("Auto Recharge?", copy=False)
    plivo_billing_mode = fields.Char("Billing Mode")
    plivo_cash_credits = fields.Char("Account Current Balance")
    plivo_log = fields.Boolean("SMS Log?", default=False, copy=False)
    
    # SO and DO Configurations
    is_confirm_so_to_send_sms = fields.Boolean("Confirm Order to Send SMS?", default=False, copy=False)
    sms_so_confirm_template_id = fields.Many2one("plivo.sms.template", "SMS Template", domain="[('model_id', '!=', False), ('model_id.model', '=', 'sale.order')]", copy=False)
    is_validate_do_to_send_sms = fields.Boolean("Validate Delivery to Send SMS?", default=False, copy=False)
    sms_do_validate_template_id = fields.Many2one("plivo.sms.template", "SMS Template", domain="[('model_id', '!=', False), ('model_id.model', '=', 'stock.picking')]", copy=False)
    
    # Magic button's fields
    sms_records_count = fields.Integer(string='Account SMS Records Count', compute='_compute_total_sms_data')
    account_sms_logs_count = fields.Integer(string='Account SMS Logs Count', compute='_compute_total_sms_data')
    
    def reset_to_new(self):
        for plivo_account in self:
            plivo_account.write({'state': 'new'})
        return True

    def action_open_sms_send_records(self):
        """
            :return: action or error
        """
        send_sms_records = self.env['plivo.sms.send'].sudo().search([('plivo_account_id', '=', self.id)])
        action = {
            'domain': "[('id', 'in', " + str(send_sms_records.ids) + " )]",
            'name': "Send SMS Records",
            'view_mode': 'tree,form',
            'res_model': 'plivo.sms.send',
            'type': 'ir.actions.act_window',
        }
        return action
    
    def action_open_sms_account_logs_records(self):
        """
            :return: action or error
        """
        account_sms_logs_records = self.env['plivo.sms.log.history'].sudo().search([('plivo_account_id', '=', self.id)])
        action = {
            'domain': "[('id', 'in', " + str(account_sms_logs_records.ids) + " )]",
            'name': "SMS Logs History",
            'view_mode': 'tree,form',
            'res_model': 'plivo.sms.log.history',
            'type': 'ir.actions.act_window',
        }
        return action

    def test_plivo_sms_connection(self):
        if not self.test_connection_mobile_number:
            raise UserError(_("'Test Connection Mobile Number' is required for connection checking!!!"))
        
        ctx = dict(self.env.context)
        method_call = ctx.get("method_call", "")
        PlivoSMSAPIObj = PlivoSMSAPI()
        response_obj = PlivoSMSAPIObj.test_plivo_sms_connection_api(self)
        
        if response_obj.status_code in [202]:
            response = response_obj.json()
            if method_call == "test_and_confirm_plivo_sms_account":
                self.state = "confirmed"
                self._cr.commit()
                return True
            error_msg = _("Service working properly!!! Your message sent successfully to %s" % (self.test_connection_mobile_number))
            raise UserError(error_msg)
        elif response_obj.status_code == 401:
            error_msg = _("Something went to wrong!!!.\nError Status Code: %s\nError Response: %s " % (response_obj.status_code, response_obj.text))
            raise UserError(error_msg)
        elif response_obj.status_code == 400:
            response = response_obj.json()
            error_msg = _("Something went to wrong!!!.\nError Status Code: %s\nError Response: %s " % (response_obj.status_code, response.get('error')))
            raise UserError(error_msg)
        else:
            error_msg = _("Something went to wrong!!!.\nError Response: %s" % (response_obj.text))
            raise UserError(error_msg)
        return True
    
    def test_and_confirm_plivo_sms_account(self):
        self.with_context({'method_call': 'test_and_confirm_plivo_sms_account'}).test_plivo_sms_connection()
        return True
    
    def get_plivo_account_details(self):
        PlivoSMSAPIObj = PlivoSMSAPI()
        response_obj = PlivoSMSAPIObj.get_plivo_sms_account_details_api(self)
        if response_obj.status_code in [200] :
            response = response_obj.json()
            self.write({
               'plivo_account_type': response.get('account_type'),
               'plivo_auto_recharge': response.get('auto_recharge', False),
               'plivo_billing_mode': response.get('billing_mode'),
               'plivo_cash_credits': response.get('cash_credits', 0.0),
            })
        elif response_obj.status_code == 401:
            error_msg = _("Something went to wrong!!!.\nError Status Code: %s\nError Response: %s " % (response_obj.status_code, response_obj.text))
            raise UserError(error_msg)
        else:
            error_msg = _("Something went to wrong!!!.\nError Response: %s" % (response_obj.text))
            raise UserError(error_msg)
        return True
    
    def send_sms_to_recipients_from_another_src(self, response_obj, message, mobile):
        plivo_sms_log_history_obj = self.env['plivo.sms.log.history']
        if response_obj.status_code in [202]:
            response = response_obj.json()
            plivo_sms_log_history_obj.create({
                'sms_send_rec_id': "",
                'plivo_account_id': self.id,
                'mobile_number': mobile,
                'message_id': response.get("message_uuid")[0],
                'message': message,
                'status': "Delivered",
            })
        elif response_obj.status_code == 401:
            plivo_sms_log_history_obj.create({
                'sms_send_rec_id': "",
                'plivo_account_id': self.id,
                'mobile_number': mobile,
                'message_id': "",
                'message': "Authentication failed.\nResponse Status Code: %s.\nError Response: %s" % (response_obj.status_code, response_obj.text),
                'status': "failed",
            })
        elif response_obj.status_code == 400:
            response = response_obj.json()
            plivo_sms_log_history_obj.create({
                'sms_send_rec_id': "",
                'plivo_account_id': self.id,
                'mobile_number': mobile,
                'message_id': "",
                'message': "A parameter is missing or is invalid.\nResponse Status Code: %s.\nError Response: %s" % (response_obj.status_code, response.get('error')),
                'status': "failed",
            })
        else:
            plivo_sms_log_history_obj.create({
                'sms_send_rec_id': "",
                'plivo_account_id': self.id,
                'mobile_number': mobile,
                'message_id': "",
                'message': "A parameter is missing or is invalid.\nError Response: %s" % (response_obj.text),
                'status': "failed",
            })
        return True