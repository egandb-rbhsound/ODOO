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
from odoo.exceptions import except_orm, Warning, RedirectWarning
from urllib3.exceptions import HTTPError
import logging
_logger = logging.getLogger(__name__)


def send_sms_using_plivo(body_sms, mob_no, from_mob=None, sms_gateway=None):
    '''
    This function is designed for sending sms using Plivo SMS API.

    :param body_sms: body of sms contains text
    :param mob_no: Here mob_no must be string having one or more number seprated by (<)
    :param from_mob: sender mobile number or id used in Plivo API
    :param sms_gateway: sms.mail.server config object for Plivo Credentials
    :return: response dictionary if sms successfully sent else empty dictionary
    '''
    if not sms_gateway or not body_sms or not mob_no:
        return {}
    if sms_gateway.gateway == "plivo":
        plivo_auth_id = sms_gateway.plivo_auth_id
        plivo_auth_token = sms_gateway.plivo_auth_token
        plivo_number = sms_gateway.plivo_number
        try:
            if plivo_auth_id and plivo_auth_token and plivo_number:
                response_dict = {}
                client = plivo.RestAPI(plivo_auth_id, plivo_auth_token)
                for mobi_no in mob_no.split('<'):
                    params = {
                        'src': plivo_number,  # Sender's phone number with country code
                        # Receivers' phone numbers with country code. The
                        # numbers are separated by "<" delimiter.
                        'dst': mobi_no,
                        'text': body_sms or "Blank Message"    # Your SMS Text Message
                    }
                    response = client.send_message(params)
                    response_dict.update({mobi_no: response})
                return response_dict
        except HTTPError as e:
            logging.info(
                '---------------Plivo HTTPError----------------------', exc_info=True)
            _logger.info(
                "---------------Plivo HTTPError While Sending SMS ----%r---------", e)
            return {}
        except Exception as e:
            logging.info(
                '---------------Plivo Exception While Sending SMS ----------', exc_info=True)
            _logger.info(
                "---------------Plivo Exception While Sending SMS -----%r---------", e)
            return {}
    return {}


def get_sms_status_for_plivo(data):
    if not data:
        return {}
    if 'message_uuid' in data and 'plivo_auth_id' in data and 'plivo_auth_token' in data:
        try:
            # Message UUID for which the details have to be retrieved
            params = {	'message_uuid': data["message_uuid"]}
            client = plivo.RestAPI(data["plivo_auth_id"], data[
                "plivo_auth_token"])
            msg_report = client.get_message(params)
            return msg_report
        except HTTPError as e:
            logging.info(
                '---------------Plivo HTTPError----------------------', exc_info=True)
            _logger.info(
                "---------------Plivo HTTPError For SMS History----%r---------", e)
            return {}
        except Exception as e:
            logging.info(
                '---------------Plivo Exception While Sending SMS ----------', exc_info=True)
            _logger.info(
                "---------------Plivo Exception For SMS History-----%r---------", e)
            return {}
    return {}


class SmsSms(models.Model):
    """SMS sending using Plivo SMS Gateway."""

    _inherit = "wk.sms.sms"
    _name = "wk.sms.sms"
    _description = "Plivo SMS"

    
    def send_sms_via_gateway(self, body_sms, mob_no, from_mob=None, sms_gateway=None):
        self.ensure_one()
        gateway_id = sms_gateway if sms_gateway else super(SmsSms, self).send_sms_via_gateway(
            body_sms, mob_no, from_mob=from_mob, sms_gateway=sms_gateway)
        if gateway_id:
            if gateway_id.gateway == 'plivo':
                plivo_auth_id = gateway_id.plivo_auth_id
                plivo_auth_token = gateway_id.plivo_auth_token
                plivo_number = gateway_id.plivo_number
                for element in mob_no:
                    for mobi_no in element.split('<'):
                        response = send_sms_using_plivo(
                            body_sms, mobi_no, from_mob=from_mob, sms_gateway=gateway_id)
                        for key in response.keys():
                            if key == mobi_no:
                                sms_report_obj = self.env["sms.report"].create(
                                    {'to': mobi_no, 'msg': body_sms, 'sms_sms_id': self.id, "auto_delete": self.auto_delete, 'sms_gateway_config_id': gateway_id.id})
                                if response[mobi_no][0] == 202:
                                    msg_uuid_list = response[
                                        mobi_no][1].get('message_uuid')
                                    message_uuid = msg_uuid_list[0]
                                    # Get SMS status
                                    msg_report = get_sms_status_for_plivo(
                                        {"message_uuid": message_uuid,  'plivo_auth_id': plivo_auth_id, 'plivo_auth_token': plivo_auth_token})
                                    msg_status = msg_report[1].get(
                                        'message_state', False)
                                    if msg_status == 'queued':
                                        sms_report_obj.write({'state': 'sent', 'plivo_message_uuid': message_uuid})
                                    elif msg_status == 'sent':
                                        sms_report_obj.write({'state': 'sent', 'plivo_message_uuid': message_uuid})
                                    elif msg_status == 'delivered':
                                        if sms_report_obj.auto_delete:
                                            sms_report_obj.unlink()
                                        else:
                                            sms_report_obj.write(
                                                {'state': 'delivered', 'plivo_message_uuid': message_uuid})
                                    else:
                                        sms_report_obj.write({'state': 'undelivered', 'plivo_message_uuid': message_uuid})
                                else:
                                    sms_report_obj.write(
                                        {'state': 'undelivered'})
                            else:
                                self.write({'state': 'error'})
                else:
                    self.write({'state': 'sent'})
            else:
                gateway_id = super(SmsSms, self).send_sms_via_gateway(
                    body_sms, mob_no, from_mob=from_mob, sms_gateway=sms_gateway)
        else:
            _logger.info(
                "----------------------------- SMS Gateway not found -------------------------")
        return gateway_id


class SmsReport(models.Model):
    """SMS report."""

    _inherit = "sms.report"

    plivo_message_uuid = fields.Char("Plivo SMS UUID")

    @api.model
    def cron_function_for_sms(self):
        _logger.info(
            "************** Cron Function For Plivo SMS ***********************")
        all_sms_report = self.search([('state', 'in', ('sent', 'new')),('sms_gateway','=','pilvo')])
        for sms in all_sms_report:
            sms_sms_obj = sms.sms_sms_id
            plivo_auth_id = sms.sms_gateway_config_id.plivo_auth_id
            plivo_auth_token = sms.sms_gateway_config_id.plivo_auth_token
            if sms.plivo_message_uuid and plivo_auth_id and plivo_auth_token:
                msg_report = get_sms_status_for_plivo(
                    {"message_uuid": sms.plivo_message_uuid, 'plivo_auth_id': plivo_auth_id, 'plivo_auth_token': plivo_auth_token})
                msg_status = msg_report[1].get('message_state')
                if msg_status == 'queued':
                    sms.write(
                        {'state': 'sent', "status_hit_count": sms.status_hit_count + 1})
                elif msg_status == 'sent':
                    sms.write(
                        {'state': 'sent', "status_hit_count": sms.status_hit_count + 1})
                elif msg_status == 'delivered':
                    if sms.auto_delete:
                        sms.unlink()
                        if sms_sms_obj.auto_delete and not sms_sms_obj.sms_report_ids:
                            sms_sms_obj.unlink()
                    else:
                        sms.write(
                            {'state': 'delivered', "status_hit_count": sms.status_hit_count + 1})
                else:
                    sms.write({'state': 'undelivered',
                               "status_hit_count": sms.status_hit_count + 1})
            else:
                sms.send_now()
        super(SmsReport, self).cron_function_for_sms()
        return True

    
    def send_sms_via_gateway(self, body_sms, mob_no, from_mob=None, sms_gateway=None):
        self.ensure_one()
        gateway_id = sms_gateway if sms_gateway else super(SmsReport, self).send_sms_via_gateway(
            body_sms, mob_no, from_mob=from_mob, sms_gateway=sms_gateway)
        if gateway_id:
            if gateway_id.gateway == 'plivo':
                plivo_auth_id = gateway_id.plivo_auth_id
                plivo_auth_token = gateway_id.plivo_auth_token
                plivo_number = gateway_id.plivo_number
                for element in mob_no:
                    count = 1
                    for mobi_no in element.split('<'):
                        if count == 1:
                            self.to = mobi_no
                            rec = self
                        else:
                            rec = self.create(
                                {'to': mobi_no, 'msg': body_sms, "auto_delete": self.auto_delete, 'sms_gateway_config_id': gateway_id.id})
                        response = send_sms_using_plivo(
                            body_sms, mobi_no, from_mob=from_mob, sms_gateway=gateway_id)
                        for key in response.keys():
                            if key == mobi_no:
                                if response[mobi_no][0] == 202:
                                    msg_uuid_list = response[
                                        mobi_no][1].get('message_uuid')
                                    message_uuid = msg_uuid_list[0]
                                    # Get SMS status
                                    msg_report = get_sms_status_for_plivo(
                                        {"message_uuid": message_uuid, 'plivo_auth_id': plivo_auth_id, 'plivo_auth_token': plivo_auth_token})
                                    msg_status = msg_report[1].get(
                                        'message_state')
                                    if msg_status == 'queued':
                                        rec.write({'state': 'sent', 'plivo_message_uuid': message_uuid})
                                    elif msg_status == 'sent':
                                        rec.write({'state': 'sent', 'plivo_message_uuid': message_uuid})
                                    elif msg_status == 'delivered':
                                        if rec.auto_delete:
                                            rec.unlink()
                                        else:
                                            rec.write({'state': 'delivered', 'plivo_message_uuid': message_uuid})
                                    else:
                                        rec.write({'state': 'undelivered', 'plivo_message_uuid': message_uuid})
                                else:
                                    rec.write({'state': 'undelivered'})
                        count += 1
                else:
                    self.write({'state': 'sent'})
            else:
                gateway_id = super(SmsReport, self).send_sms_via_gateway(
                    body_sms, mob_no, from_mob=from_mob, sms_gateway=sms_gateway)
        return gateway_id
