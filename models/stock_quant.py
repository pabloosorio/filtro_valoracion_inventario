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