## -*- coding: utf-8 -*-

from openerp import models, fields, api, _, tools
from openerp.exceptions import UserError, RedirectWarning, ValidationError
import logging
import datetime
import time
_logger = logging.getLogger(__name__)

class StockQuant(models.Model):
    _inherit ='stock.quant'
    
    stock_value= fields.Float(string="Costo", compute="_compute_stock_value", store=True)

    @api.one
    @api.depends('stock_value')
    def _compute_stock_value(self):
        self.stock_value = self.product_id.stock_value


class stock_quant_categori(models.Model):
    _inherit = 'stock.quant'

    categoria_producto = fields.Many2one('product.category', string='Categoria interna')
    peso_total = fields.Float(string="Peso Total")
    stock_actual = fields.Float(string="Stock a la fecha")
    entradas = fields.Float(string="Entradas")
    salidas = fields.Float(string="Salidas")
    ajuste = fields.Float(string="Ajustes")
    interno = fields.Float(string="M. Internos")