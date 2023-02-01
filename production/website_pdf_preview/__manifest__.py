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
{
    "name" : "Website PDF Preview",
    "version" : "14.0.0.1",
    "author" : "Geminate Consultancy Services",
    "website" : "http://www.geminatecs.com",
    "category" : "Website",
    "license": "Other proprietary", 
    "depends" : ['website'],
    "description": """
        Geminate comes with a feature to preview a any pdf document on website instead of downloading it. We are providing a quick way to review content of pdf document with single click on link or button in website. 
             It will open a popup window where you can go through the content of pdf. It supports extra tools like zoom in / out, rotate clockwise / anti-clockwise, and jump to specific page number within the pdf. 
             It is completely mobile responsive which provides a perfect view for any long pdf document with enough zooming facility and dragging along with page content.
    """,
    "summary" : """Geminate comes with a feature to preview a any pdf document on website instead of downloading it. We are providing a quick way to review content of pdf document with single click on link or button in website. 
             It will open a popup window where you can go through the content of pdf. It supports extra tools like zoom in / out, rotate clockwise / anti-clockwise, and jump to specific page number within the pdf. 
             It is completely mobile responsive which provides a perfect view for any long pdf document with enough zooming facility and dragging along with page content.""",
    'data': [
                'views/website_assets.xml',
            ],
    'qweb' : [],
    'installable': True,
    'auto_install': False,
    'price': 29.99,
    'currency': 'USD',
    'images': ['static/description/preview.jpg'],
}
