# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    total_tons_display = fields.Float(
        digits="Product Unit of Measure",
        compute="_compute_total_tons",
        store=True,
        string="Tons",
    )

    @api.depends("order_line")
    def _compute_total_tons(self):
        for rec in self:
            rec.total_tons_display = sum(rec.order_line.mapped("tons_display"))


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    tons_display = fields.Float(
        digits="Product Unit of Measure",
        compute="_compute_tons",
        store=True,
        string="Tons",
    )

    @api.depends("product_uom_qty", "product_id")
    def _compute_tons(self):
        for rec in self:
            tons = 0
            if rec.product_id:
                tons = rec.product_uom_qty * rec.product_id.weight / 1000
            rec.tons_display = tons
