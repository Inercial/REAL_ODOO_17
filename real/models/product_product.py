# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    freight_weight = fields.Float()
    tons_display = fields.Float(
        digits="Product Unit of Measure",
        compute="_compute_tons",
        string="Tons",
    )
    driver_commission = fields.Boolean(default=False)

    parent_category_id = fields.Many2one(
        related="categ_id.parent_id",
        store=True,
    )

    @api.depends("qty_available")
    @api.depends_context("from_date", "to_date")
    def _compute_tons(self):
        for rec in self:
            tons = rec.qty_available * rec.weight / 1000
            rec.tons_display = tons
