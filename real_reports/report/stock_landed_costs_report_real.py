# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockLandedCostReportReal(models.Model):
    _name = "stock.landed.cost.report.real"
    _description = "Report to show landed cost per unit"
    _auto = False
    _order = "date desc"
    _rec_name = "date"

    date = fields.Date(
        readonly=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        readonly=True,
    )
    expense_product_id = fields.Many2one(
        comodel_name="product.product",
        readonly=True,
    )
    quantity = fields.Float(
        readonly=True,
    )
    former_unit_cost = fields.Float(
        readonly=True,
        group_operator="avg",
    )
    unit_additional_landed_cost = fields.Float(
        readonly=True,
        group_operator="avg",
    )
    category_id = fields.Many2one(
        comodel_name="product.category",
        readonly=True,
    )
    parent_category_id = fields.Many2one(
        comodel_name="product.category",
        readonly=True,
    )

    _depends = {
        "stock.valuation.adjustment.lines": [
            "product_id",
            "quantity",
            "former_cost",
            "additional_landed_cost",
            "cost_id",
            "cost_line_id",
        ],
        "stock.landed.cost.lines": [
            "product_id",
        ],
        "stock.landed.cost": [
            "date",
            "state",
        ],
        "product.product": [
            "product_tmpl_id",
        ],
        "product.template": [
            "categ_id",
        ],
        "product.category": [
            "parent_id",
        ],
    }

    @property
    def _table_query(self):
        return """
            SELECT
                sval.id,
                slc.date,
                sval.product_id,
                slcl.product_id AS expense_product_id,
                sval.quantity,
                sval.former_cost / sval.quantity AS former_unit_cost,
                sval.additional_landed_cost / sval.quantity AS unit_additional_landed_cost,
                pt.categ_id AS category_id,
                pc.parent_id AS parent_category_id
            FROM
                stock_valuation_adjustment_lines AS sval
                LEFT JOIN stock_landed_cost_lines AS slcl ON sval.cost_line_id = slcl.id
                LEFT JOIN stock_landed_cost AS slc ON slc.id = sval.cost_id
                LEFT JOIN product_product AS pp ON pp.id = sval.product_id
                LEFT JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN product_category AS pc ON pt.categ_id = pc.id
            WHERE
                slc.state = 'done'
        """
