# -*- coding: utf-8 -*-
#!/usr/bin/python3
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json, requests, base64
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

PLIVO_BASE_URL_ENDPOINT = "https://api.plivo.com/v1"
PLIVO_SEND_SMS_URL_ENDPOINT = PLIVO_BASE_URL_ENDPOINT + "/Account/%s/Message/"
PLIVO_GET_ACCOUNT_DETAILS_ENDPOTINT = PLIVO_BASE_URL_ENDPOINT + "/Account/%s/"

class PlivoSMSAPI():
    
    def _get_authorization_token(self, plivo_account):
        message = "%s:%s" % (plivo_account.plivo_auth_id,plivo_account.plivo_auth_token)
        message_bytes = message.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')
        return base64_message
    
    def test_plivo_sms_connection_api(self, plivo_account):
        base64_auth = self._get_authorization_token(plivo_account)
        try:
            data = {
                "src" : plivo_account.plivo_account_from_mobile_number,
                "dst" : plivo_account.test_connection_mobile_number,
                'log': plivo_account.plivo_log,
                "text" : "Your Odoo Plivo successfully connected with Plivo."
            }
            headers = {
                "Content-type": "application/json",
                "Authorization": "Basic %s" % (base64_auth),
            }
            PLIVO_SEND_SMS_URL_ENDPOINT_FINAL = PLIVO_SEND_SMS_URL_ENDPOINT % (plivo_account.plivo_auth_id)
            response = requests.post(PLIVO_SEND_SMS_URL_ENDPOINT_FINAL, data=json.dumps(data), headers=headers, timeout=20)
            return response
        except requests.HTTPError:
            error_msg = _("Something went wrong while calling Send Plivo SMS API.")
            raise UserError(error_msg)
        except Exception as e:
            error_msg = _("Something went wrong while calling Send Plivo SMS API.\nError: %s" % (e))
            raise UserError(error_msg)
        
    def get_plivo_sms_account_details_api(self, plivo_account):
        base64_auth = self._get_authorization_token(plivo_account)
        try:
            headers = {
                "Content-type": "application/json",
                "Authorization": "Basic %s" % (base64_auth),
            }
            PLIVO_GET_ACCOUNT_DETAILS_ENDPOTINT_FINAL = PLIVO_GET_ACCOUNT_DETAILS_ENDPOTINT % (plivo_account.plivo_auth_id)
            response = requests.get(PLIVO_GET_ACCOUNT_DETAILS_ENDPOTINT_FINAL, headers=headers, timeout=20)
            return response
        except requests.HTTPError:
            error_msg = _("Something went wrong while calling GET Account Details SMS API.")
            raise UserError(error_msg)
        except Exception as e:
            error_msg = _("Something went wrong while calling GET Account Details SMS API.\nError: %s" % (e))
            raise UserError(error_msg)
        
        
    def post_plivo_sms_send_to_recipients_api(self, plivo_account, datas, src_field):
        base64_auth = self._get_authorization_token(plivo_account)
        try:
            headers = {
                "Content-type": "application/json",
                "Authorization": "Basic %s" % (base64_auth),
            }
            PLIVO_SEND_SMS_URL_ENDPOINT_FINAL = PLIVO_SEND_SMS_URL_ENDPOINT % (plivo_account.plivo_auth_id)
            response = requests.post(PLIVO_SEND_SMS_URL_ENDPOINT_FINAL, data=json.dumps(datas), headers=headers, timeout=20)
            return response
        except requests.HTTPError:
            error_msg = _("Something went wrong while calling Send Plivo SMS API.")
            raise UserError(error_msg)
        except Exception as e:
            error_msg = _("Something went wrong while calling Send Plivo SMS API.\nError: %s" % (e))
            raise UserError(error_msg)
            