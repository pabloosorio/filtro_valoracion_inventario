# -*- coding: utf-8 -*-
{
    'name': "Filtro Valoración Inventario",

    'summary': """
       Filtro de valoracion de inventario""",

    'description': """
   Inventario Rotativo por rango de fecha
    """,

    'author': "Xmarts",
    'website': "http://www.xmarts.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','product','stock_account'],
    # always loaded
    'data': [
        'views/templates.xml',
        'views/stock_quant.xml',
        'wizard/stock_quantity_filter.xml',
        #'views/product_valuation.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
