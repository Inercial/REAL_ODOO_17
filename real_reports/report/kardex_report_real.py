# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from odoo import fields, models


class KardextReportReal(models.Model):
    _name = "kardex.report.real"
    _description = "kardex Report for Real"

    name = fields.Char(
        readonly=True,
    )
    incoming = fields.Float(
        readonly=True,
    )
    outgoing = fields.Float(
        readonly=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        readonly=True,
    )
    category_id = fields.Many2one(
        related="product_id.categ_id",
        readonly=True,
        store=True,
    )
    parent_category_id = fields.Many2one(
        related="category_id.parent_id",
        readonly=True,
        store=True,
    )
    stock_valuation_layer_id = fields.Many2one(
        comodel_name="stock.valuation.layer",
        readonly=True,
    )
    account_move_id = fields.Many2one(
        related="stock_valuation_layer_id.account_move_id",
        store=True,
        readonly=True,
    )
    stock_move_id = fields.Many2one(
        related="stock_valuation_layer_id.stock_move_id",
        store=True,
        readonly=True,
    )
    origin = fields.Char(
        related="stock_valuation_layer_id.stock_move_id.origin",
        store=True,
        readonly=True,
    )
    reference = fields.Char(
        related="stock_valuation_layer_id.stock_move_id.reference",
        store=True,
        readonly=True,
    )
    accounting_date = fields.Date(
        readonly=True,
    )
    date = fields.Datetime(
        readonly=True,
    )
