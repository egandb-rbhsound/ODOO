# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import html2plaintext, plaintext2html
from odoo.addons.plivo_sms_gateway_gsc.plivo_sms_gateway_gsc_api.plivo_sms_gateway_gsc_api import PlivoSMSAPI

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    def _action_done(self):
        res = super(StockPicking, self)._action_done()
        
        plivo_sms_account = self.env['plivo.sms.gateway.account'].sudo().search([('state', '=', 'confirmed')], limit=1, order="id asc")
        if plivo_sms_account and plivo_sms_account.is_validate_do_to_send_sms and plivo_sms_account.sms_do_validate_template_id:
            PlivoSMSAPIObj = PlivoSMSAPI()
            for picking in self:
                try:
                    message = picking._message_sms_with_template_plivo(
                            template=plivo_sms_account.sms_do_validate_template_id,
                            partner_ids=picking.partner_id.ids
                        )
                    message = html2plaintext(message) #plaintext2html(html2plaintext(message))
                    data = {
                            "src": plivo_sms_account.plivo_account_from_mobile_number,
                            "dst": picking.partner_id.mobile or "",
                            'log': plivo_sms_account.plivo_log,
                            "text": message
                        }
                    response_obj = PlivoSMSAPIObj.post_plivo_sms_send_to_recipients_api(plivo_sms_account, data, "sales")
                    plivo_sms_account.send_sms_to_recipients_from_another_src(response_obj, message, picking.partner_id.mobile)
                except Exception as e:
                    picking.message_post(body=e)
        return res