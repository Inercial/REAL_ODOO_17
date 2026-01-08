# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    parent_category_id = fields.Many2one(
        related="product_id.categ_id.parent_id",
        store=True,
    )
    tons_display = fields.Float(
        digits="Product Unit of Measure",
        compute="_compute_tons",
        string="Tons",
        store=True,
    )

    @api.depends("quantity", "product_id")
    def _compute_tons(self):
        for rec in self:
            tons = 0
            if rec.product_id:
                tons = rec.quantity * rec.product_id.weight / 1000
            rec.tons_display = tons
