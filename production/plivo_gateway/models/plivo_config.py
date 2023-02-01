# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, Open Source Management Solution
# Copyright (C) 2016 webkul
# Author : www.webkul.com
#
##############################################################################

from . import plivo

from odoo import models, fields, api, _
from odoo.exceptions import except_orm
from odoo.exceptions import except_orm, Warning, RedirectWarning
from .plivo_messaging import send_sms_using_plivo
import logging
_logger = logging.getLogger(__name__)


class SmsMailServer(models.Model):
    """Configure the plivo sms gateway."""

    _inherit = "sms.mail.server"
    _name = "sms.mail.server"
    _description = "Plivo"

    plivo_number = fields.Char(string="Plivo Phone Number")
    plivo_auth_id = fields.Char(string="Plivo Auth. Id")
    plivo_auth_token = fields.Char(string="Plivo Auth. Token")

    
    def test_conn_plivo(self):
        sms_body = "Plivo Test Connection Successful........"
        mobile_number = self.user_mobile_no
        response = send_sms_using_plivo(
            sms_body, mobile_number, sms_gateway=self)
        if mobile_number in response and response.get(mobile_number)[0] == 202:
            if self.sms_debug:
                _logger.info(
                    "===========Test Connection status has been sent on %r mobile number", mobile_number)
            raise Warning(
                "Test Connection status has been sent on %s mobile number" % mobile_number)

        if mobile_number in response and response.get(mobile_number)[0] in (400, 401):
            if self.sms_debug:
                _logger.error(
                    "==========One of the information given by you is wrong. It may be [Mobile Number] [Username] or [Password] or [Api key]")
            raise Warning(
                "One of the information given by you is wrong. It may be [Mobile Number] [Username] or [Password] or [Api key]")

    @api.model
    def get_reference_type(self):
        selection = super(SmsMailServer, self).get_reference_type()
        selection.append(('plivo', 'Plivo'))
        return selection
