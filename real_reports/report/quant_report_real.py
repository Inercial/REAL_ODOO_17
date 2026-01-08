# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class QuantReportReal(models.Model):
    _name = "quant.report.real"
    _description = "Quant Report for Real"
    _auto = False
    _rec_name = "product_id"
    _order = "product_id desc"

    product_id = fields.Many2one(
        comodel_name="product.product",
        readonly=True,
    )
    default_code = fields.Char(
        readonly=True,
    )
    product_name = fields.Char(
        readonly=True,
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        readonly=True,
    )
    parent_category_id = fields.Many2one(
        comodel_name="product.category",
        readonly=True,
    )
    category_name = fields.Char(
        readonly=True,
    )
    category_id = fields.Many2one(
        comodel_name="product.category",
        readonly=True,
    )
    weight = fields.Float(
        readonly=True,
    )
    quantity = fields.Float(
        readonly=True,
    )
    tons = fields.Float(
        readonly=True,
    )
    available = fields.Float(
        readonly=True,
    )
    volume = fields.Float(
        readonly=True,
    )
    commited_qty = fields.Float(
        readonly=True,
    )
    commited_tons = fields.Float(
        readonly=True,
    )
    qty_in_production = fields.Float(
        readonly=True,
    )

    _depends = {
        "stock.quant": [
            "quantity",
        ],
        "product.category": [
            "id",
            "name",
            "parent_id",
        ],
        "stock.location": [
            "id",
        ],
        "product.template": [
            "id",
            "name",
        ],
        "product.product": [
            "id",
            "default_code",
            "weight",
            "volume",
        ],
        "stock.move": [
            "id",
            "product_uom_qty",
        ],
        "mrp.production": [
            "state",
            "product_qty",
            "product_id",
        ],
    }

    # MARCA ERROR LA QUERY
    @property
    def _table_query(self):
        return """
SELECT
res.id,
res.product_id,
res.default_code,
res.product_name,
res.category_name,
res.parent_category_id,
res.category_id,
res.weight,
res.volume,
res.quantity,
((res.quantity * res.weight) / 1000)::numeric(15,2) AS tons,
res.commited_qty,
((res.commited_qty * res.weight) / 1000)::numeric(15,2) AS commited_tons,
res.quantity - res.commited_qty AS available,
res.qty_in_production
FROM(
    SELECT
        pp.id,
        pp.id AS product_id,
        pp.default_code,
        trim(pt.name ->> 'en_US' || ' ' || COALESCE(pav.name ->> 'en_US','')) AS product_name,
        pc.name AS category_name,
        pc.parent_id AS parent_category_id,
        pc.id AS category_id,
        COALESCE(pp.weight, 0) AS weight,
        COALESCE(pp.volume, 0) as volume,
        (
            SELECT
            COALESCE(SUM(sq.quantity), 0.0)::numeric(15 ,2)
            FROM stock_quant AS sq
            WHERE
            sq.location_id IN (8, 19, 11) AND
            sq.product_id = pp.id
        ) AS quantity,
        (
            SELECT
            COALESCE(SUM(sm.product_uom_qty), 0)::numeric(15, 2)
            FROM stock_move AS sm
            WHERE
            sm.product_id = pp.id
            AND sm.location_dest_id IN (5, 24, 38, 39)
            AND sm.state NOT IN ('cancel', 'done')
        ) AS commited_qty,
        (
            SELECT COALESCE(SUM(mp.product_qty), 0)::numeric(15,2)
            FROM mrp_production AS mp
            WHERE mp.product_id = pp.id AND mp.state IN ('confirmed', 'progress', 'to_close')
        ) AS qty_in_production
    FROM product_product as pp
    LEFT JOIN product_template AS pt ON pt.id = pp.product_tmpl_id
    LEFT JOIN product_category AS pc ON pc.id = pt.categ_id
    LEFT JOIN product_variant_combination AS pvc ON pvc.product_product_id = pp.id
    LEFT JOIN product_template_attribute_value AS ptav ON ptav.id = pvc.product_template_attribute_value_id
    LEFT JOIN product_attribute_value AS pav ON pav.id = ptav.product_attribute_value_id
    WHERE
    pt.type = 'product'
    GROUP BY pp.id, pc.id, pt.id, pav.name
    ORDER BY product_name
) AS res
        """
