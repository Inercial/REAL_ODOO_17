# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    parent_category_id = fields.Many2one(
        related="product_id.categ_id.parent_id",
        store=True,
    )
    qty_min = fields.Float()
