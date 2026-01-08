# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
# pylint: skip-file

from odoo import api, fields, models


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    parent_category_id = fields.Many2one(
        related="product_id.categ_id.parent_id",
        store=True,
    )
    accounting_date = fields.Date(
        related="account_move_id.date",
        string="Accounting Date",
        store=True,
    )
    picking_type_id = fields.Many2one(
        related="stock_move_id.picking_type_id",
        store=True,
    )
    location_dest_id = fields.Many2one(
        related="stock_move_id.location_dest_id",
        store=True,
    )
    unit_cost = fields.Monetary(
        string="Unit Value",
        readonly=True,
        group_operator="avg",
    )
    tons_display = fields.Float(
        digits="Product Unit of Measure",
        compute="_compute_tons",
        string="Tons",
        store=True,
    )

    @api.depends("remaining_qty", "product_id")
    def _compute_tons(self):
        for rec in self:
            tons = 0
            if rec.product_id:
                tons = rec.remaining_qty * rec.product_id.weight / 1000
            rec.tons_display = tons
