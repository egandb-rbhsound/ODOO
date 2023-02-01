# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import html2plaintext, plaintext2html
from odoo.addons.plivo_sms_gateway_gsc.plivo_sms_gateway_gsc_api.plivo_sms_gateway_gsc_api import PlivoSMSAPI

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        
        plivo_sms_account = self.env['plivo.sms.gateway.account'].sudo().search([('state', '=', 'confirmed')], limit=1, order="id asc")
        if plivo_sms_account and plivo_sms_account.is_confirm_so_to_send_sms and plivo_sms_account.sms_so_confirm_template_id:
            PlivoSMSAPIObj = PlivoSMSAPI()
            for sale in self:
                try:
                    message = sale._message_sms_with_template_plivo(
                            template=plivo_sms_account.sms_so_confirm_template_id,
                            partner_ids=sale.partner_id.ids
                        )
                    message = html2plaintext(message) #plaintext2html(html2plaintext(message))    
                    data = {
                        "src": plivo_sms_account.plivo_account_from_mobile_number,
                        "dst": sale.partner_id.mobile or "",
                        'log': plivo_sms_account.plivo_log,
                        "text": message
                    }
                    response_obj = PlivoSMSAPIObj.post_plivo_sms_send_to_recipients_api(plivo_sms_account, data, "sales")
                    plivo_sms_account.send_sms_to_recipients_from_another_src(response_obj, message, sale.partner_id.mobile)
                except Exception as e:
                    sale.message_post(body=e)
        return res