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
    date = fields.Date('Inventory at Date', help="Choose a date to get the inventory at that date")
    idate = fields.Date('Inventory Start Date', help="Choose a date")

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
                'name': _('Inventario Rotativo'),
                'res_model': 'stock.quant',
                #"'context': dict(self.env.context, to_date=self.date),
                'context':{'fecha_inicio':self.idate,'fecha_final':self.date},
                'domain':  ['&',('create_date', '<=',  self.date),('create_date', '>=',  self.idate)],
            }
            return action
        else:
            #self.env['stock.quant']._merge_quants()
            #return self.env.ref('stock.quantsact').read()[0]
            tree_view_id = self.env.ref('stock.view_stock_quant_tree').id
            form_view_id = self.env.ref('stock.view_stock_quant_form').id
            # We pass `to_date` in the context so that `qty_available` will be computed across
            # moves until date.
            action = {
                'type': 'ir.actions.act_window',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,form',
                'name': _('Inventario Rotativo'),
                'res_model': 'stock.quant',
                #"'context': dict(self.env.context, to_date=self.date),
                'context':{'fecha_final':datetime.datetime.now()},
                'domain':  [('create_date', '<=',  datetime.datetime.now())],
            }
            return action



class stock_quant_categori(models.Model):
    _inherit = 'stock.quant'

    categoria_producto = fields.Many2one('product.category', string='Categoria interna', related='product_id.product_tmpl_id.categ_id')
    peso_total = fields.Float(string="Peso Total", compute='_compute_peso')
    stock_actual = fields.Float(string="Stock Final", compute='_compute_stock_actual')
    stock_inicial = fields.Float(string="Stock Inicial")
    entradas = fields.Float(string="Entradas")
    salidas = fields.Float(string="Salidas")
    ajuste = fields.Float(string="Ajustes")
    interno = fields.Float(string="M. Internos")


    @api.one
    @api.depends('product_id','quantity','location_id')
    def _compute_peso(self):
        peso = float(self.product_id.weight)
        cantidad = float(self.quantity)
        self.peso_total = peso * cantidad


    @api.one
    @api.depends('product_id','location_id')
    def _compute_stock_actual(self):
        cr = self.env.cr
        search_feci = self.env.context.get('fecha_inicio', False)
        search_fecf = self.env.context.get('fecha_final', False)
        if(search_fecf==False):
            search_fecf=datetime.datetime.now()
        sql=""
        sqli=""
        if(search_feci==False):
            sql = """select COALESCE((SELECT SUM(smd.product_uom_qty) 
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
                    """.format(self.product_id.id, self.location_id.id, search_fecf)
        else:
            sql = """select COALESCE((SELECT SUM(smd.product_uom_qty) 
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
                    """.format(self.product_id.id, self.location_id.id, search_fecf)
            sqli = """select COALESCE((SELECT SUM(smd.product_uom_qty) 
                   FROM stock_move smd
                   WHERE smd.state = 'done' 
                   AND smd.product_id = {0} 
                   AND smd.location_dest_id = {1}
                   AND smd.date < '{2}'),0) - COALESCE((SELECT SUM(smo.product_uom_qty) 
                   FROM stock_move smo
                   WHERE smo.state = 'done' 
                   AND smo.product_id = {0} 
                   AND smo.location_id = {1}
                   AND smo.date < '{2}'),0)
                    FROM stock_quant sq;
                    """.format(self.product_id.id, self.location_id.id, search_feci)
        cr.execute(str(sql))
        filas = cr.fetchone()
        self.stock_actual= max(filas)
        if(search_feci==False):
            self.stock_inicial = 0
        else:
            cr.execute(str(sqli))
            filas = cr.fetchone()
            self.stock_inicial= max(filas)
        sqll=""
        if(search_feci==False):
            sqll = "select sm.product_uom_qty, sp.name, sl.name, sm.location_dest_id, sm.location_id from stock_move sm full outer join stock_picking sp on sp.id=sm.picking_id full outer join stock_location sl on sl.id = sm.location_id WHERE sm.product_id='"+str(self.product_id.id)+"' and sm.date<='"+str(search_fecf)+"' and sm.state='done' and (sm.location_id='"+str(self.location_id.id)+"' or sm.location_dest_id='"+str(self.location_id.id)+"');"
        else:
            sqll = "select sm.product_uom_qty, sp.name, sl.name, sm.location_dest_id, sm.location_id from stock_move sm full outer join stock_picking sp on sp.id=sm.picking_id full outer join stock_location sl on sl.id = sm.location_id WHERE sm.product_id='"+str(self.product_id.id)+"' and sm.date<='"+str(search_fecf)+"' and sm.date>='"+str(search_feci)+"' and sm.state='done' and (sm.location_id='"+str(self.location_id.id)+"' or sm.location_dest_id='"+str(self.location_id.id)+"');"
        cr.execute(sqll)
        filas2 = cr.fetchall()
        ent = 0.0
        sal = 0.0
        aju = 0.0
        inte = 0.0
        if(filas2!=[]):
            for c in filas2:
                qty = float(c[0])
                tt = str(c[1])
                des = str(c[3])
                ori = str(c[4])
                if(tt.find("/IN/")>=0):
                    if(str(self.location_id.id)==des):
                        ent = ent + float(qty)
                if(tt.find("/OUT/")>=0):
                    if(str(self.location_id.id)==ori):
                        sal = sal + float(qty)
                if(tt == 'None'):
                    ttt = str(c[2])
                    if(ttt.find("adjustment")>=0):
                        if(str(self.location_id.id)==ori):
                            aju = aju - float(qty)
                        else:
                            aju = aju + float(qty)
                if(tt == 'None'):
                    ttt = str(c[2])
                    if(ttt.find("adjustment")>=0):
                        inte = inte
                    else:
                        if(str(self.location_id.id)==ori):
                            inte = inte - float(qty)
                        if(str(self.location_id.id)==des):
                            inte = inte + float(qty)
        self.entradas = ent
        self.salidas = sal
        self.ajuste = aju
        self.interno = inte
        