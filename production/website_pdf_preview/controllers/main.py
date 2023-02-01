# -*- coding: utf-8 -*-
###############################################################################
#
#   Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#   Copyright (C) 2016-today Geminate Consultancy Services (<http://geminatecs.com>).
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
import base64
import odoo
from odoo import http, tools
from odoo.http import request
from odoo.addons.web.controllers.main import Binary
from odoo.addons.website.controllers.main import Website
import os
import requests

    
        
        
class WebsiteInherit(Website):
     
    @http.route('/pdf_preview_modal', type='json', auth="public", website=True)
    def pdf_preview_modal(self,href, **kw):
         
        attachment_id  = False
        href_split = href.split('/web/content/')
        
        if len(href_split) > 1:
            attachment_id = href_split[1].split('?')[0]
            if attachment_id:
                attachment_record = request.env['ir.attachment'].sudo().browse(int(attachment_id))
                
                if attachment_record:
                    if attachment_record.type == 'url' and attachment_record.mimetype == 'application/pdf':
                        print("Attachement Record===1",attachment_record)
                        url_requests = requests.get(attachment_record.url, allow_redirects=True)
                        
                        with open('/tmp/url_pdf.pdf', 'wb+') as file:
                            file.write(url_requests.content)
                        
                        pdf_file = open('/tmp/url_pdf.pdf', "rb")
                        b_data = base64.b64encode(pdf_file.read()).decode('utf-8')
                        if os.path.exists('/tmp/url_pdf.pdf'):
                            os.remove('/tmp/url_pdf.pdf')
                        return {
                            'type' : attachment_record.type,
                            'url' : attachment_record.url,
                            'base64_data' : b_data,
                            'mimetype' : attachment_record.mimetype,
                            'filename' : attachment_record.name,
                            'public_pdf' : attachment_record.public,
                            'public_user' : request.env.user._is_public(),
                        }
                    elif attachment_record.type == 'binary' and attachment_record.mimetype == 'application/pdf':
                        return {
                            'type' : attachment_record.type,
                            'url' : attachment_record.url,
                            'base64_data' : attachment_record.datas.decode('utf-8') if attachment_record.datas else False,
                            'mimetype' : attachment_record.mimetype,
                            'filename' : attachment_record.name,
                            'public_pdf' : attachment_record.public,
                            'public_user' : request.env.user._is_public(),
                        }
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False
    




