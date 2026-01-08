# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MrpReportReal(models.Model):
    _name = "mrp.report.real"
    _description = "Mrp Report for Real"
    _auto = False
    _order = "name desc"

    date_start = fields.Date(
        readonly=True,
    )
    date_finished = fields.Date(
        readonly=True,
    )
    date_deadline = fields.Date(
        readonly=True,
    )
    date_planned_start = fields.Date(
        readonly=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        readonly=True,
    )
    product_name = fields.Char(
        readonly=True,
    )
    name = fields.Char(
        readonly=True,
    )
    product_qty = fields.Float(
        readonly=True,
    )
    qty_producing = fields.Float(
        readonly=True,
    )
    product_uom_qty = fields.Float(
        readonly=True,
    )
    qty_bom = fields.Float(
        readonly=True,
    )
    waste = fields.Float(
        readonly=True,
    )
    account = fields.Char(
        readonly=True,
    )
    location_src_id = fields.Many2one(
        comodel_name="stock.location",
        readonly=True,
    )
    location_dest_id = fields.Many2one(
        comodel_name="stock.location",
        readonly=True,
    )
    category_id = fields.Many2one(
        comodel_name="product.category",
        readonly=True,
    )
    category_name = fields.Char(
        readonly=True,
    )
    parent_category_id = fields.Many2one(
        comodel_name="product.category",
        readonly=True,
    )
    tons = fields.Float(
        readonly=True,
    )
    equipment_id = fields.Many2one(
        comodel_name="mrp.equipment",
        readonly=True,
    )
    equipment_name = fields.Char(
        readonly=True,
    )

    _depends = {
        "mrp.production": [
            "id",
            "name",
            "date_start",
            "date_finished",
            "date_deadline",
            "date_planned_start",
            "product_qty",
            "qty_producing",
            "product_uom_qty",
            "location_src_id",
            "location_dest_id",
        ],
        "product.product": [
            "id",
        ],
        "product.template": [
            "name",
        ],
        "stock.location": [
            "id",
            "name",
        ],
        "mrp.bom": [
            "id",
            "product_qty",
        ],
        "product.template.attribute.value": [
            "id",
            "product_attribute_value_id",
        ],
        "mrp.equipment": [
            "id",
            "name",
        ],
    }

    @property
    def _table_query(self):
        return """
            SELECT mrp.id,
                ((mrp.date_start AT TIME ZONE 'UTC') AT TIME ZONE 'America/Mexico_City')::date AS date_start,
                ((mrp.date_finished AT TIME ZONE 'UTC') AT TIME ZONE 'America/Mexico_City')::date AS date_finished,
                ((mrp.date_deadline AT TIME ZONE 'UTC') AT TIME ZONE 'America/Mexico_City')::date AS date_deadline,
                ((mrp.date_planned_start AT TIME ZONE 'UTC') AT TIME ZONE 'America/Mexico_City')::date AS date_planned_start,
                pp.id AS product_id,
                trim(pt.name ->> 'es_MX' || ' ' || coalesce(pav.name ->> 'es_MX','')) AS product_name,
                mrp.name,
                mrp.product_qty,
                mrp.qty_producing,
                mrp.product_uom_qty,
                mrpBom.product_qty AS qty_bom,
                mrp.qty_producing - mrpBom.product_qty AS waste,
                sl.name AS location_src,
                mrp.location_src_id,
                mrp.location_dest_id,
                pc.id AS category_id,
                pc.name AS category_name,
                pc.parent_id AS parent_category_id,
                (pp.weight * mrp.qty_producing) / 1000 AS tons,
                mrpP.id AS equipment_id,
                mrpP.name AS equipment_name
            FROM mrp_production AS mrp
                LEFT JOIN product_product AS pp ON pp.id = mrp.product_id
                LEFT JOIN product_template AS pt ON pt.id = pp.product_tmpl_id
                LEFT JOIN product_category AS pc ON pc.id = pt.categ_id
                LEFT JOIN stock_location AS sl ON sl.id = mrp.location_src_id
                LEFT JOIN stock_location AS sl2 ON sl2.id = mrp.location_dest_id
                LEFT JOIN mrp_bom AS mrpBom ON mrpBom.id = mrp.bom_id
                LEFT JOIN product_variant_combination pvc on pvc.product_product_id = pp.id
                LEFT JOIN product_template_attribute_value ptav on ptav.id = pvc.product_template_attribute_value_id
                LEFT JOIN product_attribute_value pav on pav.id = ptav.product_attribute_value_id
                LEFT JOIN mrp_equipment AS mrpP ON mrpP.id = mrp.equipment_id
            WHERE mrp.state = 'done'
        """
