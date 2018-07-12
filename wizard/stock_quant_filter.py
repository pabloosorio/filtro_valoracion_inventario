# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import datetime
import time


class StockQuantFilter(models.TransientModel):
    _name = 'stock.quant.filter'
    _description = 'Valoración de Inventario con Filtros'

    compute_at_date = fields.Selection([
        (0, 'Mostrar todo el inventario'),
        (1, 'Filtrar por fecha')
    ], string="Compute", help="Muestra con filtros el inventario")
    date = fields.Datetime('Inventory at Date', help="Choose a date to get the inventory at that date")

    def open_table(self):
        self.ensure_one()

        if self.compute_at_date:
            tree_view_id = self.env.ref('stock.view_stock_quant_tree').id
            form_view_id = self.env.ref('stock.view_stock_quant_form').id
            # We pass `to_date` in the context so that `qty_available` will be computed across
            # moves until date.
            action = {
                'type': 'ir.actions.act_window',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,form',
                'name': _('Valoracion de inventario v10'),
                'res_model': 'stock.quant',
                #"'context': dict(self.env.context, to_date=self.date),
                'context':{'search_default_internal_loc': 1, 'search_default_locationgroup':1,'fecha_prueba':self.date},
                'domain':  [('create_date', '<=',  self.date)],
            }
            return action
        else:
            self.env['stock.quant']._merge_quants()
            return self.env.ref('stock.quantsact').read()[0]

class stock_quant_categori(models.Model):
    _inherit = 'stock.quant'

    categoria_producto = fields.Many2one('product.category', string='Categoria interna', related='product_id.product_tmpl_id.categ_id', store=True)
    peso_total = fields.Float(string="Peso Total", compute='_compute_peso')
    stock_actual = fields.Float(string="Stock a la fecha", compute='_compute_stock_actual')

    @api.one
    @api.depends('peso_total','product_id','quantity')
    def _compute_peso(self):
        peso = float(self.product_id.weight)
        cantidad = float(self.quantity)
        self.peso_total = peso * cantidad

    @api.one
    @api.depends('product_id','location_id')
    def _compute_stock_actual(self):
        cr = self.env.cr
        search_fec = self.env.context.get('fecha_prueba', False)
        if(search_fec==False):
            search_fec= datetime.datetime.now()
        sql = """SELECT COALESCE((SELECT SUM(smd.product_uom_qty) 
               FROM stock_move smd
               WHERE smd.state = 'done' 
               AND smd.product_id = {0} 
               AND smd.location_dest_id = {1}
               AND smd.date <= '{2}'),0) - COALESCE((SELECT SUM(smo.product_uom_qty) 
               FROM stock_move smo
               WHERE smo.state = 'done' 
               AND smo.product_id = {0} 
               AND smo.location_id = {1}
               AND smo.date <= '{2}'),0)
                FROM stock_quant sq;
                """.format(self.product_id.id, self.location_id.id, search_fec)
        cr.execute(str(sql))
        filas = cr.fetchone()
        total_stock = max(filas)
        '''sql = "select sm.product_uom_qty, sp.name, sl.name from stock_move sm full outer join stock_picking sp on sp.id=sm.picking_id full outer join stock_location sl on sl.id = sm.location_id WHERE sm.product_id='"+str(self.product_id.id)+"' and sm.date<='"+str(search_fec)+"' and sm.state='done' and (sm.location_id='"+str(self.location_id.id)+"' or sm.location_dest_id='"+str(self.location_id.id)+"');"
        cr.execute(str(sql))
        filas = cr.fetchall()
        total_stock = 0.0
        if(filas!=[]):
            for c in filas:
                qty = float(c[0])
                tt = str(c[1])
                if(tt.find("/IN/")>=0):
                    total_stock = total_stock + float(qty)
                if(tt == 'None'):
                    ttt = str(c[2])
                    if(ttt.find("adjustment")>=0):
                        total_stock = total_stock + float(qty)
                    else:
                        total_stock = total_stock - float(qty)
                if(tt.find("/OUT/")>=0):
                    total_stock = total_stock - float(qty)'''
        self.stock_actual = total_stock