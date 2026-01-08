# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    tons_display = fields.Float(
        digits="Product Unit of Measure",
        compute="_compute_tons",
        store=True,
        string="Tons",
    )

    @api.depends("product_id", "quantity", "product_uom_qty")
    def _compute_tons(self):
        for rec in self:
            tons = 0
            if rec.product_id:
                quantity = rec.product_uom_qty
                if rec.quantity:
                    quantity = rec.quantity
                tons = quantity * rec.product_id.weight / 1000
            rec.tons_display = tons


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    tons_display = fields.Float(
        digits="Product Unit of Measure",
        compute="_compute_tons",
        store=True,
        string="Tons line",
    )

    @api.depends("product_id", "quantity")
    def _compute_tons(self):
        for rec in self:
            tons = 0
            if rec.product_id:
                tons = rec.quantity * rec.product_id.weight / 1000
            rec.tons_display = tons
