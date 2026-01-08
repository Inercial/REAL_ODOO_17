# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProductionConsumptionReportReal(models.Model):
    _name = "production.consumption.report.real"
    _description = "Production Consumption Report for Real"
    _auto = False
    _order = "name desc"

    product_id = fields.Many2one(
        comodel_name="product.product",
        readonly=True,
    )
    product_uom_qty = fields.Float(readonly=True, string="Quantity")
    date = fields.Date(
        readonly=True,
    )
    equipment_id = fields.Many2one(
        comodel_name="mrp.equipment",
        readonly=True,
    )

    _depends = {
        "mrp.production": [
            "id",
            "equipment_id",
        ],
        "product.product": [
            "id",
            "product_tmpl_id",
        ],
        "product.template": [
            "id",
            "categ_id",
        ],
        "stock.move": ["id", "product_id", "product_uom_qty", "date", "raw_material_production_id"],
    }

    @property
    def _table_query(self):
        return """
            SELECT
                sm.id,
                sm.product_id,
                sm.product_uom_qty,
                ((sm.date AT TIME ZONE 'UTC') AT TIME ZONE 'America/Mexico_City')::date AS date,
                mrp.equipment_id
            FROM stock_move as sm
            LEFT JOIN product_product AS pp ON pp.id = sm.product_id
            LEFT JOIN product_template AS pt ON pt.id = pp.product_tmpl_id
            LEFT JOIN mrp_production AS mrp ON mrp.id = sm.raw_material_production_id
            WHERE sm.raw_material_production_id IS NOT NULL
            AND sm.state = 'done'
            AND pt.categ_id IN (14, 19)
        """
